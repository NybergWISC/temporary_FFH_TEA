# First iteration of Fusion Sensitivity Study (with tokamak variables)

import numpy as np
import os
import shutil
import sys
import subprocess

fusion_data = np.loadtxt(fname='reducedFusionSheet.csv', delimiter="|", dtype=str)

run_dir = os.getcwd()

# print(fusion_data)
indices = fusion_data[1:,0]
var_names = fusion_data[1:,1]
values = fusion_data[1:,2]
units = fusion_data[1:,3]

validRows = []
invalidRows = []

runs = {
    "half" : 0.5
}


""" "original" : 1.0,    
    "zero" : 0.0,
    "double": 2.0,
    "half" : 0.5,
    "tenX" : 10.0
} """

# From ACCERT/src/etc/accert.sch
usefulUnits = ['m', 'kA', 'm3', 'amu', 'A', 'kg', 'N/A', 'M$', 'm2', 'T', 'years', '$/m', '($/J wall plug)', 'MW', 'M$/MJ', 'kg/m3', 'kg/m4', 'kg/m5', 'kg/m6', 'kg/m7', 'kg/m8', 'kg/m9', 'kg/m10', 'kg/m11', 'K', 'keV', 'C', 'J', 'A/W', 'MJ', 'GJ', 'fraction of tritium fused/target', 'reactions/m3/sec', 'W', '', 'days', 'Hz', 'MA-turns', 'A/m2', 'reactions/sec', 'kW', 'sec', 's', 'M$/m3', '$', '$/W', '$/kVA', '$/kg', '$/A-m', 'M$/vol', '$/10000m3/hr', '$/w', 'M$/year/1200MW', '$/m2', '($/W)', '$/m3', '$/kA-m', '$/MVA', '$/kW', '$/circuit', '$/MJ', '$/channel', '$/target', '$/J', '$/coil', '$/A', 'kV', 'kg/coil']

# All arrays to capture the specific errors
error_convert_units = []
error_type = []
error_value = []
error_process = []
error_schema = []
error_nesting_schema = []

vars_in_sch = ['a', 'acptmax', 'admvol', 'afuel', 'ai', 'aintmass', 'akappa', 'areaoh', 'awpoh', 'b0', 'blmass', 'cconfix', 'cconshpf', 'cconshtf', 'cdirt', 'cdriv0', 'cdriv1', 'cdriv2', 'cdriv3', 'cfind_0', 'cfind_1', 'cfind_2', 'cfind_3', 'cland', 'clgsmass', 'coilmass', 'convol', 'coolmass', 'coolwh', 'cowner', 'cpstcst', 'cpttf', 'crypmw', 'cryvol', 'csi', 'cturbb', 'd_0', 'd_1', 'd_2', 'd_3', 'dcdrv0', 'dcdrv1', 'dcdrv2', 'dcond_0', 'dcond_1', 'dcond_2', 'dcond_3', 'dcond_4', 'dcond_5', 'dcond_6', 'dcond_7', 'dcond_8', 'dcopper', 'dens', 'divcst', 'divsur', 'dlscal', 'drbi', 'dtstor', 'dvrtmass', 'ealphadt', 'echarge', 'echpwr', 'edrive', 'effrfss', 'elevol', 'ensxpfm', 'esbldgm3', 'estotftgj', 'etadrv', 'expel', 'expepe', 'exphts', 'exprb', 'exprf', 'exptpe', 'faccd', 'faccdfix', 'fachtmw', 'fburn', 'fcap0', 'fcdfuel', 'fcontng', 'fcsht', 'fcuohsu', 'fcupfsu', 'fkind', 'fncmass', 'fndt', 'ftrit', 'fusionrate', 'fwallcst', 'fwarea', 'fwmass', 'fwmatm', 'gain', 'gsmass', 'hccl', 'hcwt', 'helpow', 'hrbi', 'i_tf_sc_mat', 'i_tf_sup', 'iblanket', 'iefrf', 'ife', 'ifedrv', 'ifueltyp', 'imax', 'iohcl', 'ipfres', 'ireactor', 'istore', 'isumatoh', 'isumatpf', 'itart', 'l1', 'lpulse', 'lsa', 'ltot', 'mbvfac', 'mcdriv', 'n_tf', 'n_tf_turn', 'nohc', 'nphx', 'ntype', 'nvduct', 'oh_steel_frac', 'pacpmw', 'palpnb', 'peakmva', 'pfbldgm3', 'pfckts', 'pfmass', 'pfwdiv', 'pfwndl', 'pgrossmw', 'pheat', 'pibv', 'pinjht', 'pinjwp', 'plascur', 'plhybd', 'pnbitot', 'pnetelmw', 'pnucblkt', 'pnucshld', 'powfmw', 'pthermmw', 'r0', 'rbrt', 'rbvfac', 'rbvol', 'rbwt', 'reprat', 'ric_0', 'ric_1', 'ric_2', 'ric_3', 'ric_4', 'ric_5', 'ric_6', 'rjconpf_0', 'rjconpf_1', 'rjconpf_2', 'rjconpf_3', 'rjconpf_4', 'rjconpf_5', 'rjconpf_6', 'rjconpf_7', 'rjconpf_8', 'rjconpf_9', 'rjconpf_10', 'rjconpf_11', 'rjconpf_12', 'rjconpf_13', 'rjconpf_14', 'rjconpf_15', 'rjconpf_16', 'rjconpf_17', 'rjconpf_18', 'rjconpf_19', 'rjconpf_20', 'rjconpf_21', 'rpf_0', 'rpf_1', 'rpf_2', 'rpf_3', 'rpf_4', 'rpf_5', 'rpf_6', 'shmatm', 'spfbusl', 'srcktpm', 'stcl', 'tdown', 'tdspmw', 'tf_h_width, ', 'tfacmw', 'tfbusl', 'tfbusmas', 'tfcbv', 'tfckw', 'tfcmw', 'tfhmax', 'tfleng', 'tfmass', 'tlvpmw', 'tmpcry', 'trcl', 'trithtmw', 'triv', 'turns_0', 'turns_1', 'turns_2', 'turns_3', 'turns_4', 'turns_5', 'turns_6', 'twopi', 'ucad', 'ucaf', 'ucahts', 'ucap', 'ucblbe', 'ucblbreed', 'ucblli', 'ucblli2o', 'ucbllipb', 'ucblss', 'ucblvd', 'ucbpmp', 'ucbus', 'uccarb', 'uccase', 'ucco', 'ucconc', 'uccpcl1', 'uccpclb', 'uccpmp', 'uccr', 'uccry', 'uccryo', 'uccu', 'ucdgen', 'ucdiv', 'ucdtc', 'ucduct', 'ucech', 'ucel', 'ucf1', 'ucfnc', 'ucfpr', 'ucfwa', 'ucfwps', 'ucfws', 'ucgss', 'uchrs', 'uchts_0', 'uchts_1', 'uciac', 'ucich', 'ucint', 'uclh', 'uclv', 'ucmb', 'ucme', 'ucmisc', 'ucnbi', 'ucnbv', 'ucpens', 'ucpfb', 'ucpfbk', 'ucpfbs', 'ucpfcb', 'ucpfdr1', 'ucpfic', 'ucpfps', 'ucphx', 'ucpp', 'ucrb', 'ucsc_0', 'ucsc_1', 'ucsc_2', 'ucsc_3', 'ucsc_4', 'ucsc_5', 'ucsc_6', 'ucsc_7', 'ucsc_8', 'ucsh', 'ucshld', 'ucswyd', 'uctfbr', 'uctfbus', 'uctfdr', 'uctfgr', 'uctfic', 'uctfps', 'uctfsw', 'uctpmp', 'uctr', 'ucturb_0', 'ucturb_1', 'ucvalv', 'ucvdsh', 'ucviac', 'ucwindpf', 'ucwindtf', 'umass', 'vacdshm', 'vachtmw', 'vcdimax', 'vf', 'vfohc', 'vol', 'volrci', 'vpfskv', 'vpumpn', 'vtfskv', 'vvmass', 'wgt2', 'whtblbe', 'whtblbreed', 'whtblli', 'whtblss', 'whtblvd', 'whtcas', 'whtconcu', 'whtconsc', 'whtcp', 'whtpfs', 'whtshld', 'whttflgs', 'wpenshld', 'wrbi', 'wsvfac', 'wsvol', 'wtblli2o', 'wtbllipb', 'rmbvol', 'ucws', 'shovol', 'expcry']

numSuccess = 0
successfulRuns = []
numFails = 0

errors = []
added_vars = []


# sys.stdout = open("output_sensitivityStudies.out", "w")
# Open the template file and rip down
with open('fusionSensitivityTemplate.son', 'r') as template_file:
    try:
        shutil.rmtree("./sensitivity_outs")
    except:
        print("First Run")
    finally:
        os.mkdir("./sensitivity_outs")
    templateLines = template_file.readlines()

# Nested loops of doom. Do all runs for all lines
for rows in fusion_data[1:]:
    print(f"{rows[1]}")
    try:
        if str(rows[1]) not in vars_in_sch:
            added_vars.append(rows[1])
            # raise ValueError(f"Variable \"{rows[1]}\" not in ACCERT schema")
        if float(rows[2]) < 0:
            raise ValueError(f"Variable {rows[1]} value is less than 0: {rows[2]}")
        # if str(rows[3]) == "N/A":
        #     raise ValueError("Unhandled unit \"N/A\"")
        os.mkdir(f"./sensitivity_outs/{rows[1]}")
        os.chdir(f"./sensitivity_outs/{rows[1]}")
        for run_key in runs.keys():
            with open(f'temp_fusion_input_{rows[1]}_{run_key}.son', 'w') as temp_input_file:
                tempLines = templateLines
                if rows[2]:
                    tempLines[6] = f"    var(\"{rows[1]}\")" + "{" + f"value = {float(rows[2])*runs[run_key]} unit = {rows[3]}" + "}\n"
                    temp_input_file.writelines(tempLines)
            subprocess.run(["python3", "/home/mnyberg/Desktop/installs/ACCERT/src/Main_modified.py", "-i", f"temp_fusion_input_{rows[1]}_{run_key}.son"], check = True)
            # subprocess.run(["python3", "/home/mnyberg/Desktop/installs/ACCERT/src/Main.py", "-i", f"temp_fusion_input_{rows[1]}_{run_key}.son"], check = True)
            # os.system(f"python3 /home/mnyberg/Desktop/installs/ACCERT/src/Main_modified.py -i temp_fusion_input_{rows[1]}_{run_key}.son")
            os.rename("output.out", f"output_{rows[1]}_{run_key}.out")
    except ValueError as eV:
        error_value.append(rows[1])
        error_convert_units.append(rows[3])
        errors.append(str(eV))
        numFails=numFails+1
    except TypeError as eT:
        error_type.append(rows[1])
        errors.append(str(eT))
        numFails=numFails+1
    except subprocess.CalledProcessError as eP:
        error_process.append(rows[1])
        errors.append(str(eP))
        numFails=numFails+1
        if "results[" in str(eP):
            error_type.append(rows[1])
        elif "unexpected invalid token" in str(eP):
            error_schema.append(rows[1])
            if "[ or {" in str(eP):
                error_nesting_schema.append(rows[1])
    except Exception as e:
        # print(f"\n{e}\n")
        errors.append(str(eT))
        numFails=numFails+1
    else:
        numSuccess=numSuccess+1
        successfulRuns.append(rows[1])
    if os.getcwd() is not run_dir:
        os.chdir(run_dir)

    # os.rename("fusion_updated_account.xlsx", f"fusion_updated_acccount_{rows[1]}_{run_key}.xlsx")
# print(errors)
print(f"Number of successes: {numSuccess}")
print(f"Number of failures: {numFails}")
print(errors)

# print(all_units)

print(f"{len(successfulRuns)} successful runs. Variables: {successfulRuns}")
print(f"{len(error_convert_units)} unit conversion errors. Variables: {error_value} Units:{error_convert_units}")

print(f"{len(error_process)} subprocess errors. Variables: {error_process}")
print(f"    {len(error_type)} type errors. Variables: {error_type}")
print(f"    {len(error_schema)} schema errors. Variables: {error_schema}")
print(f"    {len(error_nesting_schema)} nesting schema ([] expected) errors. Variables: {error_nesting_schema}")


# for vars in added_vars:
#     print(f"\'{vars}\' ", end="")

# Copy all successful runs to another folder
try:
    shutil.rmtree("./good_outs")
except:
    print("First Output")
finally:
    os.mkdir("./good_outs")
for good_var in successfulRuns:
    shutil.copytree(f"./sensitivity_outs/{good_var}/", f"./good_outs/{good_var}/")
