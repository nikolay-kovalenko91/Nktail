from distutils.core import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='nktail',
      version='0.1',
      description='A custom Unix tail program implementation',
      long_description=readme(),
      url='https://github.com/nikolay-kovalenko91/Nktail',
      author='Nikolay Kovalenko',
      author_email='nikolay.kovalenko91@gmail.com',
      license='MIT',
      packages=['nktail'],
      install_requires=[
          'click',
      ],
      entry_points={
          'console_scripts': ['nktail=nktail.command_line:main'],
      },
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
