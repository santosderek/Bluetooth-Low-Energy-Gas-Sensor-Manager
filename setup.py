from setuptools import setup, find_packages

setup(name='CMUT Graph Sensor Manager',
      version='0.1',
      description='CMUT Graph Sensor Manager',
      author='Derek Santos',
      url='https://github.com/santosderek/Bluetooth-Low-Energy-Gas-Sensor-Manager',
      packages=['sensor_client'],
      scripts=['sensor_client/main.py',
               'sensor_client/main_window.py',
               'sensor_client/sensor.py',
               'sensor_client/config.py'],
      entry_points={
        'console_scripts':
            ['sensormanager = main:main']
      },
      install_requires=['pyqtgraph==0.10.0', 'PyQt5==5.9']
     )
