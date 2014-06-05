import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'nut2',
    ]

setup(name='webNUT',
      version='0.0',
      description='webNUT',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: System :: Power (UPS)",
        ],
      author='george2',
      author_email='rpubaddr0@gmail.com',
      url='https://github.com/george2/webNUT',
      keywords='web pyramid pylons nut network ups tools',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="webnut",
      entry_points="""\
      [paste.app_factory]
      main = webnut:main
      """,
      )
