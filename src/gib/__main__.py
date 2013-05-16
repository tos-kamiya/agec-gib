# coding: utf-8

'''
Created on 2013/05/16

@author: toshihiro
'''

import re
import sys
import os.path as p

sys.path.insert(0, p.join(p.dirname(p.abspath(__file__)), '..'))
import clonefile_manip as cm

sourcefile_directories = []
clonedata_filenames = []
clonedata_options = []
clonedata_opeseq_traces = []

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html", 
            clonetracefile=clonedata_filenames[0],
            options=clonedata_options,
            opeseq_traces=clonedata_opeseq_traces)

@app.route('/src/<path:filename>')
def show_sourcefile(filename):
    try:
        target = int(request.args['target'])
    except:
        target = -1
    path = p.join(sourcefile_directories[0], filename)
    with open(path, 'rb') as f:
        ls = f.read().decode('utf-8')
    linedata = ls.replace('\t', '    ').split('\n')
    return render_template("sourcecode.html", 
            filename=filename, linedata=linedata, target=target)

def main(argv):
    from argparse import ArgumentParser
    psr = ArgumentParser(description="Agec's Global-inspired clone browser")
    psr.add_argument('srcdir', nargs=1)
    psr.add_argument('clonetracefile', nargs=1,
            help="clone trace data with line numbers. specify '-' to read from stdin")
    psr.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = psr.parse_args(argv[1:])
    
    sourcefile_directories.append(args.srcdir[0])
    clonedata_filenames.append(args.clonetracefile[0])
    opeseq_traces = []
    sys.stderr.write("> reading clone-trace file\n")
    for tag, value in cm.read_clone_file_iter(clonedata_filenames[0]):
        if tag == cm.OPTIONS:
            clonedata_options.extend(value.format())
        elif tag == cm.OPESEQ_TRACES:
            opeseq_traces.append(value)
        else:
            assert False

    pat = re.compile(r"([^:]+):\s*(\d+)\s*>\s*(\d+)\s*//\s*(.+)")
    def scan_trace_item(s):
        m = pat.match(s)
        assert m
        source_file = m.group(1)
        line_num = int(m.group(2))
        depth = int(m.group(3))
        invoked_method = m.group(4)
        return source_file, line_num, depth, invoked_method
    
    for opeseq, traces in opeseq_traces:
        d = (opeseq, [tuple(map(scan_trace_item, trace)) for trace in traces])
        clonedata_opeseq_traces.append(d)

    app.debug = True
    app.run()

if __name__ == '__main__':
    main(sys.argv)