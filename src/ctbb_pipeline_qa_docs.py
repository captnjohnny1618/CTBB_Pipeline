import sys
import os

import glob
import jinja2

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
import pypeline as pype
from pypeline import load_config

def usage():
    print('  usage: ctbb_pipeline_qa_docs.py /path/to/config/file.yml /path/to/library')
    print('       Generate HTML quality-assurance documents to quickly review')
    print('       test results.')    
    print('    Copyright (c) John Hoffman 2017')

if __name__=="__main__":

    if len(sys.argv)!=3:
        usage()        
    else:
        # Get our command line arguments and instantiate the pipeline library
        config_filepath=sys.argv[1]
        library_dirpath=sys.argv[2]
        config=load_config(config_filepath)
        library=ctbb_plib(library_dirpath)

        # Get list of reconstructions and dictionary with patient ids
        recon_list=library.get_recon_list()
        case_list = library.__get_case_list__() # two way dictionary with file hashes (to look up patient id)

        # Iterate through all reconstructions and build paths to QA image files
        qa_files=[]
        data=[]
        for r in recon_list:

            # Get patient raw file hash and internal ID
            patient_hash=r['pipeline_id']
            patient_id=os.path.splitext(os.path.basename(case_list[patient_hash]))[0]

            # Set up our paths (based on the img series filepath)
            img_series_filepath=os.path.join(library.path,r["img_series_filepath"])
            img_dirpath=os.path.dirname(img_series_filepath)
            series_dirpath=os.path.dirname(img_dirpath)
            qa_dirpath=os.path.join(series_dirpath,'qa')

            # If the first image series
            # Get a list of all QA files that we have (one image per test)
            if not qa_files:
                qa_files=os.listdir(qa_dirpath)
                print(qa_files)
                
            # Files that we can QA to start with (more in the future):
            ##     image.png   - reconstruction quality
            ##     overlay.png - segmentation quality
            ##     RA-950.png  - RA-950 scoring
            # Build a dictionary of paths for each file in the qa directory
            qa_filepaths={}
            for f in qa_files:
                qa_filepaths[os.path.splitext(f)[0]]=os.path.join(qa_dirpath,f)

            data_dict=qa_filepaths
            data_dict["id"]=patient_id
            
            data.append(data_dict)

        # We want to make one page for each metric/test
        for f in qa_files:
            output_filename="results_{}_{}.html".format(os.path.splitext(f)[0],)
            output_path=os.path.join(library.path,'qa',)
            
            loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(os.path.abspath(__file__)))
            env = jinja2.Environment(loader=loader)
            vars = {
                "data":data,
            }
            template = env.get_template("template.tpl")


            
            with open("results.html", "w") as f:
                f.write(template.render(vars))
