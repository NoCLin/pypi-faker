import zipfile
import hashlib
import base64
from io import BytesIO

def get_file_hash(file_content):
    sha256_hash = hashlib.sha256(file_content.encode()).digest()
    base64_encoded = base64.b64encode(sha256_hash).decode()
    return base64_encoded.rstrip('=')

def create_record(files):
    record_lines = []
    for filename, content in files.items():
        if filename.endswith("RECORD"):
            record_lines.append(f"{filename},,")
        else:
            record_lines.append(f"{filename},sha256={get_file_hash(content)},{len(content)}")
    return "\n".join(record_lines)

def create_wheel_file(package_name, version):

    wheel_filename = f"{package_name}-{version}-py3-none-any.whl"
    dist_info_dir = f"{package_name}-{version}.dist-info"
    files = {}
    files[f'setup.py'] = "#"
    files[f'{dist_info_dir}/METADATA'] = f"""Metadata-Version: 2.1
Name: {package_name}
Version: {version}

"""
    files[f'{dist_info_dir}/WHEEL'] =  f"""Wheel-Version: 1.0
Generator: custom
Root-Is-Purelib: true
Tag: py3-none-any
"""
    files[f'{dist_info_dir}/top_level.txt'] = "\n"
    files[f'{dist_info_dir}/RECORD'] = ""
    files[f'{dist_info_dir}/RECORD'] = create_record(files)
    byte_stream = BytesIO()
    with zipfile.ZipFile(byte_stream, 'w', zipfile.ZIP_DEFLATED) as wheel:
        
        for filename, content in files.items():
            wheel.writestr(filename, content)
    byte_stream.seek(0)
    content = byte_stream.read()
    byte_stream.close()
    return wheel_filename, content

if __name__ == "__main__":
    package_name = 'dummies'
    version = '0.1'
    print(create_wheel_file(package_name, version))