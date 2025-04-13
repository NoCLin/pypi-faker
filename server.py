import io
import os
import tarfile
import tempfile

import httpx
from bs4 import BeautifulSoup, Comment
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse

from wheel_generator import create_wheel_file

app = FastAPI(debug=False)


def make_package(name: str, version: str = '0.1', format='targz'):
	regex = r'^[a-zA-Z0-9_-]+$'
	version_regex = r'^[a-zA-Z0-9._-]+$'
	import re
	if not re.match(regex, name):
		raise ValueError('Invalid appname')
	if not re.match(version_regex, version):
		raise ValueError('Invalid version')

	fc = f"""
from setuptools import setup
setup(
    name='{name}',
    version='{version}',
)
"""
	if format == 'whl':

		with tempfile.TemporaryDirectory() as tmpdir:


			setup_py = os.path.join(tmpdir, 'setup.py')
			readme_md = os.path.join(tmpdir, 'README.md')
			with open(setup_py, 'w') as f:
				f.write(fc)
			with open(readme_md, 'w') as f:
				f.write("created by pypi-faker")

			# wheel_name = f'{name}-{version}-py3-none-any.whl'
			# wheel_path = os.path.join(tmpdir, wheel_name)
			# from build.__main__ import build_package_via_sdist
			# build_package_via_sdist(srcdir=tmpdir,outdir=tmpdir,distributions=['wheel'],isolation=False, skip_dependency_check=True)
			# open(wheel_path,"rb").read()

			_, content = create_wheel_file(name, version,)
			return content

	elif format == 'targz':

		tar_buffer = io.BytesIO()
		with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
			tarinfo = tarfile.TarInfo(name='fake/setup.py')
			tarinfo.size = len(fc)
			tarinfo.mtime = 0
			tar.addfile(tarinfo, io.BytesIO(fc.encode()))

		return tar_buffer.getvalue()
	else:
		raise ValueError('Invalid format')


@app.get('/')
async def root(request: Request):
	url = request.url
	root = f'{url.scheme}://{url.hostname}'
	return HTMLResponse(f"Hello World! <br> try"
													 f" `pip install {root}/targz/torch/1.0` or `pip install torch==2.0.0 -i {root}`")


@app.get('/{name}/')
async def package_page(name: str, request: Request):
	if name in ['setuptools', 'pip', 'wheel']:
		return RedirectResponse(f'https://pypi.org/simple/{name}/')

	# Fetch package page from PyPI
	async with httpx.AsyncClient() as client:
		response = await client.get(f'https://pypi.org/simple/{name}/')
		html = response.text

	# Update links to point to our server
	soup = BeautifulSoup(html, 'html.parser')
	origin_html = str(soup.find("html"))

	for link in soup.find_all('a'):
		url = link.get('href')
		if url:
			file_name = link.text

			if file_name.endswith('.whl'):
				file_stem = file_name.removesuffix('.whl')
			elif file_name.endswith('.tar.gz'):
				file_stem = file_name.removesuffix('.tar.gz')
			else:
				raise ValueError('Invalid file name')

			parts = file_stem.split('-')
			package_name = parts[0]
			version = parts[1]

			# new_file_name = f'{package_name}-{version}.tar.gz'
			# new_url = f'/targz/{package_name}/{version}/{new_file_name}'

			new_file_name = f'{package_name}-{version}-py3-none-any.whl'
			new_url = f'/whl/{package_name}/{version}/{new_file_name}'
			link.attrs = {'href': new_url}

			link.string = new_file_name

		comment = Comment('Original: ' + origin_html)
		soup.insert(-1, comment)

	return Response(content=str(soup), media_type='text/html')


@app.get('/targz/{name}/{version}')
async def get_targz_package_short(name: str, version: str):
	filename = f'{name}-{version}.tar.gz'
	return RedirectResponse(f'/targz/{name}/{version}/{filename}')


@app.get('/targz/{name}/{version}/{filename}')
async def get_targz_package(name: str, version: str, filename: str):
	content = make_package(name, version, format="targz")
	headers = {
		'Content-Disposition': f'filename={filename}',
		'Content-Type': 'octet-stream'
	}
	return Response(content=content, headers=headers)


@app.get('/whl/{name}/{version}')
async def get_whl_package_short(name: str, version: str):
	filename = f'{name}-{version}-py3-none-any.whl'
	return RedirectResponse(f'/whl/{name}/{version}/{filename}')


@app.get('/whl/{name}/{version}/{filename}')
async def get_whl_package(name: str, version: str, filename: str):
	content = make_package(name, version, format="whl")
	headers = {
		'Content-Disposition': f'filename={filename}',
		'Content-Type': 'octet-stream'
	}
	return Response(content=content, headers=headers)


if __name__ == '__main__':
	import uvicorn

	uvicorn.run('server:app', reload=True, port=8000)
