import { Hono } from 'hono';

// @ts-ignore
import { tar } from './tinytar';
import { load } from 'cheerio';
import { gzip } from 'pako';

async function makePackage(name: string, version = '0.1') {
	const regex = /^[a-zA-Z0-9_-]+$/;
	const versionRegex = /^[a-zA-Z0-9._-]+$/;
	if (!regex.test(name)) {
		throw new Error('Invalid appname');
	}
	if (!versionRegex.test(version)) {
		throw new Error('Invalid version');
	}

	const fc = `
from setuptools import setup
setup(
    name='${name}',
    version='${version}',
)
`;

	return gzip(tar([
		{
			name: 'fake/setup.py',
			data: fc,
			modifyTime: new Date(0)
		}
	]));
}


const app = new Hono();

app.get('/', async c => {
	const url = new URL(c.req.url);
	const root = `${url.origin}`;
	return c.body(`Hello World! try \`pip install ${root}/targz/torch/1.0\` or \`pip install torch==2.0.0 -i ${root}\` `);
});

// package page
app.get('/:name/', async c => {
	const { name } = c.req.param();
	// build from source (.tar.gz) requires the following packages
	if (['setuptools', 'pip', 'wheel'].includes(name)) {
		return c.redirect('https://pypi.org/simple/' + name);
	}

	const response = await fetch('https://pypi.org/simple/' + name, {
		headers: {
			'User-Agent': c.req.header('User-Agent') || ''
		}
	});

	const html = await response.text();

	const $ = load(html);

	$('a').each((i, elem) => {
		const url = $(elem).attr('href') || '';
		const fileName = $(elem).text();
		Array.from(Object.keys($(elem).attr()!))
			.filter(key => key != 'href')
			.map(key => $(elem).removeAttr(key));

		const parts = fileName.split('-');
		const packageName = parts[0]; // TODO: check if it's the same as the name
		const version = parts[1];

		// convert all links to our server in tar.gz format
		const newFileName = `${packageName}-${version}.tar.gz`;
		const newUrl = `/targz/${packageName}/${version}/` + newFileName;
		$(elem).attr('href', newUrl);
		$(elem).text(newFileName);
	});

	return c.body($.html(), {
		headers: {
			'content-type': 'text/html'
		}
	});
});


// TODO: support wheel.
//  But it's not easy to generate without a python environment

app.get('/targz/:name/:version', async c => {
	const { name, version } = c.req.param();
	const content = await makePackage(name, version);
	return c.redirect(`/targz/${name}/${version}/${name}-${version}.tar.gz`);
});

app.get('/targz/:name/:version/:filename', async c => {
	const { name, version, filename } = c.req.param();

	const content = await makePackage(name, version);

	const headers = {
		'Content-Disposition': `filename=${filename}`,
		'Content-Type': 'octet-stream'
	};

	return c.body(content, { headers });
});


export { app };
