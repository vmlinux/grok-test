#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pygrok
import argparse
import logging
import os

#define log colors
COLOR_RED='\033[1;31m'
COLOR_GREEN='\033[1;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[1;34m'
COLOR_PURPLE='\033[1;35m'
COLOR_CYAN='\033[1;36m'
COLOR_GRAY='\033[1;37m'
COLOR_WHITE='\033[1;38m'
COLOR_RESET='\033[1;0m'

LOG_COLORS = {
    'DEBUG': '%s',
    'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
    'WARNING': COLOR_YELLOW + '%s' + COLOR_RESET,
    'ERROR': COLOR_RED + '%s' + COLOR_RESET,
    'CRITICAL': COLOR_RED + '%s' + COLOR_RESET,
    'EXCEPTION': COLOR_RED + '%s' + COLOR_RESET,
}
class ColoredFormatter(logging.Formatter):
    '''A colorful formatter.'''
    def __init__(self, fmt = None, datefmt = None):
        logging.Formatter.__init__(self, fmt, datefmt)
    def format(self, record):
        level_name = record.levelname
        msg = logging.Formatter.format(self, record)
        return LOG_COLORS.get(level_name, '%s') % msg

#define grok-test project
class grokprj(object):
	def __init__(self,dir):
		self.home=dir
		self.custpattern_dir=os.path.join(dir,'patterns')
		self.datapattern_file=os.path.join(dir,'datapattern')
	def create_prj(self):
		try:
			logging.info('init prj {0}'.format(self.home))
			if os.path.isdir(self.home):
				logging.error('dir {0} already exists, skip'.format(self.home))
			else:
				os.makedirs(self.custpattern_dir)
				with open(self.datapattern_file,'w') as df:
					df.write('%{REPLACEHERE}')
				logging.info('prj {0} created'.format(self.home))
		except Exception,e:
			logging.warning('({0}){1}'.format(e.__class__.__name__,e))
			logging.error('error create prj {0}'.format(self.home))
	def create_conf(self):
		if self.check_prj():
			try:
				logging.info('create conf for prj {0}'.format(self.home))
				match_lines=[]
				with open(self.datapattern_file,'r') as df:
					for line in df.read().splitlines():
						match_lines.append('			message => "{0}"'.format(line.strip()))
				fn=os.path.join(self.home,'80-{0}.conf'.format(os.path.basename(self.home)))
				with open(fn,'w') as cf:
					cf.write(
'''input {
	stdin {}
}
filter {
	grok {
		patterns_dir => "/path/to/%s"
		match => {
%s
		}
		overwrite => ["message"]
	}
}
output {
	stdout {
		codec => rubydebug
	}
}
''' % (self.custpattern_dir,'\n'.join(match_lines))
							)
				logging.info('copy {0} and patterns subdir to logstash'.format(fn))
			except Exception,e:
				logging.warning('({0}){1}'.format(e.__class__.__name__,e))
				logging.error('error create conf for prj {0}'.format(self.home))
	def check_prj(self):
		logging.info('check prj {0}'.format(self.home))
		if os.path.isdir(self.home) and os.path.isfile(self.datapattern_file):
			for file in os.listdir(self.custpattern_dir):
				self.check_custpattern_file(os.path.join(self.custpattern_dir,file))
			with open(self.datapattern_file,'r') as df:
				for line in df.read().splitlines():
					self.check_custpattern_sample('@',line.strip())
			return True
		else:
			logging.error('prj {0} not exits or damaged'.format(self.home))
			return False
	def check_custpattern_file(self,file):
		logging.info('check custpattern file : {0}'.format(file))
		if os.path.isfile(file):
			with open(file,'r') as pf:
				for line in pf.read().splitlines():
					self.check_custpattern_item(line)
	def check_custpattern_item(self,line):
		#logging.info('check custpattern item : {0}'.format(line))
		pname,pattern=line.split(' ',1)
		self.check_custpattern_sample(pname.strip(),pattern.strip())
	def check_custpattern_sample(self,pname,pattern):
		logging.info('check pattern {0} => {1}'.format(pname,pattern if pname=='@' else '...'))
		file_count=0
		try:
			for file in os.listdir(self.home):
				fn=os.path.join(self.home,file)
				if os.path.isfile(fn) and file.endswith('log') and file.startswith('sample'):
					file_count+=1
					self.check_sample_pattern(fn,pname,pattern)
		except Exception,e:
			logging.error('errors in custom pattern {0} => {1}'.format(pname,pattern))
		if file_count==0:
			logging.error('no sample found in {0}'.format(self.home))
			exit(1)
	def check_sample_pattern(self,logfile,pname,pattern):
		#logging.info('check sample {0}'.format(logfile))
		line_count=0
		match_count=0
		with open(logfile,'r') as lf:
			for line in lf.read().splitlines():
				m=pygrok.grok_match(line,pattern,custom_patterns_dir=self.custpattern_dir)
				line_count+=1
				if m is not None:
					match_count+=1
					if pname=='@':
						print '  {0}) {2}{1}{3}'.format(line_count,line,COLOR_WHITE,COLOR_RESET)
						print '    => {0}'.format(m)
				else:
						print '  {0}) {2}{1}{3}'.format(line_count,line,COLOR_RED,COLOR_RESET)
		match_percent=match_count*100/line_count
		if match_percent==100:
			logging.info('{1} : match percent {0} %'.format(match_percent,logfile))
		elif match_percent>90:
			logging.warning('{1} : match percent {0} %'.format(match_percent,logfile))
		else:
			logging.error('{1} : match percent {0} %'.format(match_percent,logfile))

def grokprj_init(dirs):
	for dir in dirs:
		prj=grokprj(dir)
		prj.create_prj()

def grokprj_check(dirs):
	for dir in dirs:
		prj=grokprj(dir)
		prj.check_prj()

def grokprj_logstash(dirs):
	for dir in dirs:
		prj=grokprj(dir)
		prj.create_conf()

def app():
	parser=argparse.ArgumentParser(description='''
		grok check:
		$ %(prog)s -init syslog
		$ %(prog)s syslog nginx
''',formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('dir',nargs='+',
		help='[REQUIRED] dir contains check files')
	parser.add_argument('-i','--init',action='store_true',
		help='[OPTIONAL] init dir with file structure')
	parser.add_argument('-l','--logstash',action='store_true',
		help='[OPTIONAL] create a logstash config file')
	args=parser.parse_args()
	if args.init:
		grokprj_init(args.dir)
	elif args.logstash:
		grokprj_logstash(args.dir)
	else:
		grokprj_check(args.dir)

def init_log(file):
	logFormat='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
	logging.basicConfig(level=logging.INFO,
		format=logFormat,
		#datefmt='%Y-%m-%d %h:%M:%S',
		filename=file,
		filemode='a')
	logConsole=logging.StreamHandler();
	logConsole.setLevel(logging.INFO)
	logConsole.setFormatter(ColoredFormatter('%(levelname)s %(message)s'))
	logging.getLogger('').addHandler(logConsole)

if __name__=='__main__':
	init_log('grok-check.log')
	app()
