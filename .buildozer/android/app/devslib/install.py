import os

f = open(os.path.expanduser('~/.bashrc'), 'a')
f.write('export PYTHONPATH=' + os.path.join(os.getcwd(), 'www.devsinc.com.mx' , 'devslib') )
f.close()
