from setuptools import setup, find_packages
import os
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        for dependancy in f.read().splitlines():
            if dependancy[:4]=='git+':
                packageName=dependancy.split('/')[-1]
                dependancy=packageName+" @ "+dependancy
            install_requires.append(dependancy)

if __name__ == "__main__":
    setup(
        name='cognitoclaims',
        packages=find_packages(),
        install_requires=install_requires
    )