import os, sys

overwrite=False
# overwrite=True

xsec_script_folder=os.getcwd()+"/genproductions/test/calculateXSectionAndFilterEfficiency/" # change this folder
json_output_folder=os.getcwd()+"/json/" # change this folder

os.system("mkdir -p "+json_output_folder)

with open('datasets.txt') as f:
    for dataset in f:
        dataset = dataset.rstrip('\n')
        primary_dataset_name = dataset.split("/")[1]
        print primary_dataset_name
        if not os.path.isfile("xsec/xsec_"+primary_dataset_name+".log"):
            print "Input file not found"
        else:
            # check the xsec log file
            if not os.path.isfile(json_output_folder+"/xsec_"+primary_dataset_name+".json") or overwrite:
                with open("xsec/xsec_"+dataset.split('/')[1]+".log", 'r+') as f:
                    content = f.read()
                    if not 'final cross section' in content: 
                        print "Cross section computation not correctly performed, skipping"
                        os.system("echo "+dataset+" >> dataset_noxsec.txt")
                        if not 'Successfully opened file' in content:
                            os.system("echo "+dataset+" >> dataset_filenotfound.txt")
                        continue
            # check the existing json file
            if os.path.isfile(json_output_folder+"/xsec_"+primary_dataset_name+".json"):
                with open(json_output_folder+"/xsec_"+dataset.split('/')[1]+".json", 'r') as f:
                    content = f.read()
                    # if '"accuracy": "none"' in content:
                        # with open(json_output_folder+"/xsec_"+dataset.split('/')[1]+".json", 'r+') as f2:
                            # f2.write(content.replace('"accuracy": "none"','"accuracy": "unknown"'))
                    if (not 'REPLACE_' in content) \
                        and (not '"accuracy": "none",' in content) \
                        and (not "\"MCM\": \"\"," in content) \
                        and (not "\"MCM\": \"None\"," in content): 
                        # and (not "CITo" in primary_dataset_name) \
                        print "json OK, skipping"
                        continue
                    else:
                        print "json corrupted, reproducing"
                        print content
            os.system("cp test_xsecdb_insert.json "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            os.system("sed -i -e 's/REPLACE_PRIMARY_DATASET_NAME/"+primary_dataset_name+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            os.system("sed -i -e 's/REPLACE_FULL_DATASET_NAME/"+dataset.replace("/","\/")+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            cross_section = os.popen("strings xsec/xsec_"+primary_dataset_name+".log | grep final\ cross\ section").read().replace("pb","").replace(" ","").rstrip().split("=")[1].split("+-")
            os.system("sed -i -e 's/REPLACE_CROSS_SECTION/"+str(float(cross_section[0]))+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            # xsec_uncertainty = float(cross_section[1])/float(cross_section[0])*100. # percent
            xsec_uncertainty = float(cross_section[1]) # absolute in pb
            os.system("sed -i -e 's/REPLACE_TOTAL_UNCERTAINTY/"+str(xsec_uncertainty)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            equivalent_lumi_grep = os.popen("strings xsec/xsec_"+primary_dataset_name+".log | grep equivalent\ lumi").read()
            if equivalent_lumi_grep != "":
                equivalent_lumi = float(equivalent_lumi_grep.replace("pb","").replace(" ","").rstrip().split("=")[1].split("+-")[0])
                os.system("sed -i -e 's/REPLACE_EQUIVALENT_LUMI/"+str(equivalent_lumi)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            neg_weight_grep = os.popen("strings xsec/xsec_"+primary_dataset_name+".log | grep fraction\ of\ events\ with\ negative\ weights").read()
            if neg_weight_grep != "":
                negative_weights = float(neg_weight_grep.replace("pb","").replace(" ","").rstrip().split("=")[1].split("+-")[0])
                os.system("sed -i -e 's/REPLACE_FRACTION_NEGATIVE_WEIGHT/"+str(negative_weights)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            center_of_mass_energy = primary_dataset_name.split("TeV")[len(primary_dataset_name.split("TeV"))-2].rsplit("_",1)
            if len(center_of_mass_energy) > 1 and center_of_mass_energy[-1].isdigit():
                center_of_mass_energy = int(center_of_mass_energy[-1])
            # print 'center_of_mass_energy',center_of_mass_energy
            if center_of_mass_energy in [0.9,7,8,13,14]:
                os.system("sed -i -e 's/REPLACE_ENERGY/"+str(center_of_mass_energy)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            matrix_element = "none"
            # "accuracy": "incorrect option selected. Allowed: ['LO', 'NLO', 'NNLO', 'NNNLO', 'unknown']"
            accuracy = "unknown"
            shower = "none"
            if "powheg" in primary_dataset_name:
                matrix_element = "Powheg"
                accuracy = "NLO"
            elif "madgraph" in primary_dataset_name:
                matrix_element = "Madgraph"
                accuracy = "LO"
            elif "amcnlo" in primary_dataset_name:
                matrix_element = "Madgraph"
                accuracy = "NLO"
            elif "sherpa" in primary_dataset_name:
                matrix_element = "Sherpa"
                shower = "Sherpa"
                accuracy = "NLO"
            if "pythia8" in primary_dataset_name:
                shower = "Pythia8"
                if matrix_element == "":
                    matrix_element = "Pythia8"
                    accuracy = "LO"
                    
            os.system("sed -i -e 's/REPLACE_MATRIX_ELEMENT/"+str(matrix_element)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            os.system("sed -i -e 's/REPLACE_PARTON_SHOWER/"+str(shower)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            os.system("sed -i -e 's/REPLACE_ACCURACY/"+str(accuracy)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            # mcm_prepid = os.popen('/cvmfs/cms.cern.ch/common/das_client --query="mcm dataset='+dataset+'"').read().rsplit('\n',2)[1]
            mcm_prepid = os.popen('wget -qO- https://cms-pdmv.cern.ch/mcm/public/restapi/requests/produces'+dataset).read()
            # print 'mcm_prepid',mcm_prepid
            if len(mcm_prepid) > 1 and "-" in mcm_prepid:
                print mcm_prepid.split('prepid')[1].split(',')[0]
                mcm_prepid = mcm_prepid.split('prepid')[1].split(',')[0].replace('\": ',"").replace('\"',"")
                print mcm_prepid
                os.system("sed -i -e 's/REPLACE_MCM_PREPID/"+str(mcm_prepid)+"/g' "+json_output_folder+"/xsec_"+primary_dataset_name+".json")
            
            with open(json_output_folder+"/xsec_"+dataset.split('/')[1]+".json", 'r+') as f:
                print "produced json:\n", f.read()
            # sys.exit()

    
