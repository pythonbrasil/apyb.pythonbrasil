from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='apyb.pythonbrasil',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone apyb pythonbrasil web event conference',
      author='Erico Andrei <erico@simplesconsultoria.com.br>',
      author_email='products@simplesconsultoria.com.br',
      url='https://github.com/pythonbrasil/apyb.pythonbrasil',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['apyb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.theming',
          'Products.Maps==2.1.1',
          'collective.simplesocial==1.6',
          'Products.PloneFormGen',
          'sc.social.like',
          'apyb.registration',
          'apyb.papers',
          'webcouturier.dropdownmenu==2.1'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
