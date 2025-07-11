# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import scipy
import pandas as pd
import json
import pkg_resources

# This code is based off the ARPA-E PyFECONS code, available at
# https://github.com/Woodruff-Scientific-Ltd/ARPAE-PyFECONS

# THIS VERSION OF THE CODE WAS EDITED TO ONLY INCLUDE COA 2 TO BETTER COMPARE WITH OTHER CODES

# Physical constants
E_DT = 17.59e6 * 1.60218*10**-19 # J
E_alpha = 3.52e6 * 1.60218*10**-19 # J
E_n = E_DT - E_alpha # J
m_T = 3.01604928 * 1.66053907*10**-27 # kg, triton mass
m_D = 2.01410177811 * 1.66053907*10**-27 # kg, deuteron mass
m_6Li = 6.0151228874 * 1.66053907*10**-27 # kg, lithium-6 mass

# Conversion factors
Wh_to_BTU = 3.41214 # 1 Wh = 3.41214 BTU

class cost_account:
    """
    A class that tracks the cost of a fusion plant.
    
    This is essentially a wrapper for a pandas DataFrame.
    
    
    """    
    
    def __init__(self):
        self.data = pd.DataFrame()
        # self.data.index.rename('account_number', inplace=True)
        
    def add_account(self, account_number, account_name, cost):
        """
        Add an account to the cost_account object.

        Parameters
        ----------
        account_number : str, float, or int
            Account number.  For example, '22.1.1'
        account_name : str
            Account name.  For example, 'First Wall and Blanket'
        cost : float
            Cost of the associated account in MUSD.

        Returns
        -------
        None.

        """
        
        try:
            if (int(str(account_number).split('.')[0]) % 10) == 0:
                indentation = 0
            else:
                indentation = account_number.count('.') + 1
        except:
            indentation = 0
        indented_name = '    ' * indentation + account_number + ' ' + account_name
        
        
        self.data = pd.concat([self.data, pd.DataFrame(
            index=[account_number], 
            data={'Level':[indentation],
                  'Account Name':[account_name], 
                  'Indented Name':[indented_name],
                  'Cost':[cost]})])
        self.data.index.name = 'Account Number'
        
    # Deleted: def add_total(self):
        

def generate_report(
    application='heat',
    P_f = 0,
    P_f_L = 0,
    P_NBI=0, P_ECH=0, P_ICRH=0,
    construction_time=6,
    NOAK=False,
    n_unit=False,
    lifetime=30, replacement=10, availability=0.90, discount=0.0245,
    cost_file='woodruff-data.csv', method='new',
    include_tax=False,
    include_decommissioning=False,
    include_licensing=False,
    include_contingency=False,
    save=True,
    verbose=True,
    vacuum_gap_CC=0.01,
    first_wall_material='W',
    first_wall_thickness=0.01,
    vacuum_vessel_material='SS316',
    vacuum_vessel_thickness=0.01,
    multiplier_material='Pb',
    multiplier_thickness=0.01,
    blanket_coolant_material='Natural PbLi',
    blanket_thickness=1.00,
    blanket_coolant_fraction=0.90,
    blanket_structural_material='SS316',
    blanket_structural_fraction=0.10,
    outer_vessel_thickness=0.01,
    **kwargs):
    
    """
    Generate a report based on user input.
    
    Parameters
    ----------
    application : str, optional
        The application, either 'electricity' or 'heat'. 
        This changes the power balance and some reporting. The default 
        is 'heat'.
    P_f : float
        The total fusion power in MW.  The length of the central cell 
        is scaled to achieve this value. This is not the net electrical power!
    P_f_L : float
        The central cell linear fusion power in MW/m. 
    P_NBI : float 
        The applied NBI power in MW.  
    P_ECH : float
        The applied ECH power in MW.  
    P_ICRH : float
        The applied ICRH power in MW.  
    construction_time : int
        The construction time in years.  The default is 6.
    NOAK : bool
        Whether this is an NOAK device.  The default is False.  
        This will probably be deprecated soon.
    n_unit : int or bool
        The number of the tandem unit, in terms of first of a kind (1), 
        second of a kind (2), etc.  When this is False, the FOAK cost is used.
        The default is False.
    lifetime : int 
        The lifetime of the tandem in years.  This is used for LCOE and LCOH 
        calcualtions.  The default is 30.
    replacement : int 
        The replacement interval of the magnets in years.  The default is 10.
    availability : float
        The facility availability. The range is between 0 and 1, inclusive.
        The default is 0.90.
    cost_file : str
        The filename of the cost file.  The default is 'woodruff-data.csv'.
    method : str
        The power balance method.  The default is 'new'.  
        This will be deprecated soon.
    include_tax : bool
        Whether to include tax.  The default is False.
    include_decommissioning : bool
        Whether to include decommissioning.  The default is False.
    include_licensing : bool
        Whether to include licensing.  The default is False.
    include_contingency : bool
        Whether to include continency.  The default is False
    save : bool
        Whether to save results.  The default is True
    verbose : bool
        Whether to print a lot.  The default is True
    vacuum_gap_CC : float
        The vacuum gap in the central cell, in meters.  The default is 0.01.
    first_wall_material : str
        The first wall material.  The default is 'W'.
    first_wall_thickness : float
        The first wall thickness, in meters.  The default is 0.01.
    vacuum_vessel_material : str
        The vacuum vessel material.  The default is 'SS316'.
    vacuum_vessel_thickness : float
        The vacuum vessel thickness, in meters.  The default is 0.01.
    multiplier_material : str
        The muliplier material.  The default is 'Pb'
    multiplier_thickness : float
        The multiplier thickness, in meters.  The default is 0.01.
    blanket_coolant_material : str
        The blanket coolant material.  The default is 'Natural PbLi'.
    blanket_thickness : float
        The blanket thickness, in meters.  The default is 1.00.
    blanket_coolant_fraction : float
        The blanket coolant fraction, from 0 to 1.  The default is 0.90.
    blanket_structural_material : str
        The blanket structural material.  The default is 'SS316'.
    blanket_structural_fraction : float
        The blanket structural fraction, from 0 to 1.  The default is 0.10.
    outer_vessel_thickness : float
        The outer vessel thickness, in meters.  The default is 0.01.

    Returns
    -------
    pandas.DataFrame with:
        'P_fusion [MW]'
        'L_CC [m]'
        'P_in [MW]'
        'P_net,e [MW]'
        'P_heat [MW]'
        'Q_sci'
        'Q_e'
        'CapEx [MUSD]'
    Also either of the following depending on application:   
        'LCOE [USD/MWh]'                              
        'LCOH [USD/MMBTU]'
    """
    
    inputs = generate_inputs(
        application=application,
        P_f=P_f, P_f_L=P_f_L,
        P_NBI=P_NBI, P_ECH=P_ECH, P_ICRH=P_ICRH,
        N_module=1, NOAK=NOAK, n_unit=n_unit, save=save,
        lifetime=lifetime, replacement=replacement, 
        availability=availability, cost_file=cost_file, 
        method=method, construction_time=construction_time,
        include_tax=include_tax,
        include_decommissioning=include_decommissioning,
        include_licensing=include_licensing, include_contingency=include_contingency,
        discount=discount,
        
        vacuum_gap_CC=vacuum_gap_CC,
        first_wall_material=first_wall_material,
        first_wall_thickness=first_wall_thickness,
        vacuum_vessel_material=vacuum_vessel_material,
        vacuum_vessel_thickness=vacuum_vessel_thickness,
        multiplier_material=multiplier_material,
        multiplier_thickness=multiplier_thickness,
        blanket_coolant_material=blanket_coolant_material,
        blanket_thickness=blanket_thickness,
        blanket_coolant_fraction=blanket_coolant_fraction,
        blanket_structural_material=blanket_structural_material,
        blanket_structural_fraction=blanket_structural_fraction,
        outer_vessel_thickness=outer_vessel_thickness,
        **kwargs
        )

    # Create cost data object
    cost_data = cost_account()
    
    # Using nTtau Digital Definitions, but not necessarily calculations
    # https://github.com/Woodruff-Scientific-Ltd/ARPAE-PyFECONS
    """ cost_data.add_account('10', 'Pre-Construction Costs', Account_C10(inputs))
    cost_data.add_account('11', 'Land and Land Rights', Account_C11(inputs))
    cost_data.add_account('12', 'Site Permits', Account_C12(inputs))
    cost_data.add_account('13', 'Plant Licensing', Account_C13(inputs))
    cost_data.add_account('14', 'Plant Permits', Account_C14(inputs))
    cost_data.add_account('15', 'Plant Studies', Account_C15(inputs))
    cost_data.add_account('16', 'Plant Reports', Account_C16(inputs))
    cost_data.add_account('17', 'Other Pre-Construction Costs', Account_C17(inputs))
    cost_data.add_account('19', 'Contingency on Pre-Construction Costs', Account_C19(inputs)) """
    
    cost_data.add_account('20', 'Capitalized Direct Costs (CDC)', Account_C20(inputs))
    
    cost_data.add_account('21', 'Structures and Improvements', Account_C21(inputs))
    cost_data.add_account('21.1', 'Site Preparation/Yard Work', Account_C21_1(inputs))
    cost_data.add_account('21.2', 'Heat Island Building', Account_C21_2(inputs))
    cost_data.add_account('21.3', 'Turbine Generator Building', Account_C21_3(inputs))
    cost_data.add_account('21.4', 'Heat Exchanger Building', Account_C21_4(inputs))    
    cost_data.add_account('21.5', 'Power Supply and Energy Storage', Account_C21_5(inputs)) 
    cost_data.add_account('21.6', 'Reactor Auxiliaries', Account_C21_6(inputs)) 
    cost_data.add_account('21.7', 'Hot Cell', Account_C21_7(inputs)) 
    cost_data.add_account('21.8', 'Reactor Services', Account_C21_8(inputs)) 
    cost_data.add_account('21.9', 'Service Water', Account_C21_9(inputs)) 
    cost_data.add_account('21.10', 'Fuel Storage', Account_C21_10(inputs)) 
    cost_data.add_account('21.11', 'Control Room', Account_C21_11(inputs)) 
    cost_data.add_account('21.12', 'Onsite AC Power', Account_C21_12(inputs)) 
    cost_data.add_account('21.13', 'Administration', Account_C21_13(inputs)) 
    cost_data.add_account('21.14', 'Site Services', Account_C21_14(inputs)) 
    cost_data.add_account('21.15', 'Cryogenics', Account_C21_15(inputs)) 
    cost_data.add_account('21.16', 'Security', Account_C21_16(inputs)) 
    cost_data.add_account('21.17', 'Ventilation Stack', Account_C21_17(inputs)) 
    
    cost_data.add_account('22', 'Heat Island Plant Equipment', Account_C22(inputs))
    
    cost_data.add_account('22.1', 'Heat Island Components', Account_C22_1(inputs))
    cost_data.add_account('22.1.1', 'First Wall and Blanket', Account_C22_1_1(inputs))
    cost_data.add_account('22.1.2', 'Magnet Radiation Shield', Account_C22_1_2(inputs))
    
    cost_data.add_account('22.1.3', 'Coils', Account_C22_1_3(inputs))
    cost_data.add_account('22.1.3.1', 'HF Coils', Account_C22_1_3_1(inputs))
    cost_data.add_account('22.1.3.2', 'LF Coils', Account_C22_1_3_2(inputs))
    cost_data.add_account('22.1.3.3', 'CC Coils', Account_C22_1_3_3(inputs))
    
    cost_data.add_account('22.1.4', 'Supplemental Heating', Account_C22_1_4(inputs))
    cost_data.add_account('22.1.4.1', 'NBI', Account_C22_1_4_1(inputs))
    cost_data.add_account('22.1.4.2', 'ICRH', Account_C22_1_4_2(inputs))
    cost_data.add_account('22.1.4.3', 'ECH', Account_C22_1_4_3(inputs))    
    
    cost_data.add_account('22.1.5', 'Primary Structure and Support', Account_C22_1_5(inputs))
    
    cost_data.add_account('22.1.6', 'Vacuum System', Account_C22_1_6(inputs))
    # cost_data.add_account('22.1.6.1', 'Vacuum Vessel', Account_C22_1_6_1(inputs))
    cost_data.add_account('22.1.6.2', 'Vessel Refrigerators', Account_C22_1_6_2(inputs))
    cost_data.add_account('22.1.6.3', 'Primary Vacuum Pumps', Account_C22_1_6_3(inputs))
    cost_data.add_account('22.1.6.4', 'Backing Vacuum Pumps', Account_C22_1_6_4(inputs))
    
    cost_data.add_account('22.1.7', 'Power Supplies', Account_C22_1_7(inputs))
    cost_data.add_account('22.1.8', 'Divertor', Account_C22_1_8(inputs))
    cost_data.add_account('22.1.9', 'Direct Energy Convertor', Account_C22_1_9(inputs))
    cost_data.add_account('22.1.11', 'Assembly and Installation Costs', Account_C22_1_11(inputs))
    # cost_data.add_account('22.1.19', 'Scheduled Replacement Cost', 0)
    
    cost_data.add_account('22.2', 'Main and Secondary Coolant', Account_C22_2(inputs))
    cost_data.add_account('22.3', 'Auxiliary Cooling Systems', Account_C22_3(inputs))
    cost_data.add_account('22.4', 'Radioactive Waste Treatment', Account_C22_4(inputs))
    cost_data.add_account('22.5', 'Fuel Handling and Storage', Account_C22_5(inputs))
    cost_data.add_account('22.6', 'Other Heat Island Equipment', Account_C22_6(inputs))
    cost_data.add_account('22.7', 'Instrumentation and Control', Account_C22_7(inputs))
    
    cost_data.add_account('23', 'Turbine Plant Equipment', Account_C23(inputs))
    cost_data.add_account('24', 'Electric Plant Equipment', Account_C24(inputs))
    cost_data.add_account('25', 'Miscellaneous Plant Equipment', Account_C25(inputs))
    cost_data.add_account('26', 'Heat Rejection', Account_C26(inputs))
    cost_data.add_account('27', 'Special Materials', Account_C27(inputs))
    cost_data.add_account('28', 'Digital Twin/Simulator', Account_C28(inputs))
    cost_data.add_account('29', 'Contingency on Direct Capital Costs', Account_C29(inputs))
    
    # FOCUS ONLY ON COA 2
    """ cost_data.add_account('30', 'Capitalized Indirect Service Costs (CISC)', Account_C30(inputs))
    cost_data.add_account('31', 'Field Indirect Costs', Account_C31(inputs))
    cost_data.add_account('32', 'Construction Supervision', Account_C32(inputs))
    cost_data.add_account('33', 'Commissioning and Start-Up Costs', Account_C33(inputs))
    cost_data.add_account('34', 'Demonstration Test Run', Account_C34(inputs))
    cost_data.add_account('35', 'Design Services Offsite', Account_C35(inputs))
    cost_data.add_account('36', 'PM/CM Services Offsite', Account_C36(inputs))
    cost_data.add_account('37', 'Design Servies Offsite', Account_C37(inputs))
    cost_data.add_account('38', 'PM/CM Services Onsite', Account_C38(inputs))
    cost_data.add_account('39', 'Contingency on Support Services', Account_C39(inputs))
    
    cost_data.add_account('40', 'Capitalized Owner\'s Cost (COC)', Account_C40(inputs))
    # cost_data.add_account('41', 'Staff Recruitment and Training', Account_C41(inputs))
    # cost_data.add_account('42', 'Staff Housing', Account_C42(inputs))
    # cost_data.add_account('43', 'Staff Salary-Related Costs', Account_C43(inputs))
    # cost_data.add_account('44', 'Other Owner\'s Costs', Account_C44(inputs))
    # cost_data.add_account('49', 'Contingency on Owner\'s Costs', Account_C49(inputs))
    
    cost_data.add_account('50', 'Capitalized Supplementary Costs (CSC)', Account_C50(inputs))
    cost_data.add_account('51', 'Shipping and Transportation Costs', Account_C51(inputs))
    cost_data.add_account('52', 'Spare Parts', Account_C52(inputs))
    cost_data.add_account('53', 'Taxes', Account_C53(inputs))
    cost_data.add_account('54', 'Insurance', Account_C54(inputs))
    cost_data.add_account('55', 'Initial Fuel Load', Account_C55(inputs))
    cost_data.add_account('58', 'Decommissioning Costs', Account_C58(inputs))
    cost_data.add_account('59', 'Contingency on Supplementary Costs', Account_C59(inputs))
    
    cost_data.add_account('60', 'Capitalized Financial Costs (CFC)', Account_C60(inputs))
    cost_data.add_account('61', 'Escalation', Account_C61(inputs))
    cost_data.add_account('62', 'Fees', Account_C62(inputs))
    cost_data.add_account('63', 'Interest During Construction (IDC)', Account_C63(inputs))
    cost_data.add_account('69', 'Contingency on Capitalized Financial Costs', Account_C69(inputs))
    
    cost_data.add_account('OCC', 'Overnight Capital Cost (OCC)', Account_OCC(inputs))
    
    cost_data.add_account('TCC', 'Total Capital Cost (TCC)', Account_TCC(inputs))
    
    cost_data.add_account('O&M', 'Operations and Maintenance', Account_C70(inputs))
    cost_data.add_account('Fuel', 'Fuel', Account_C80(inputs))
    
    cost_data.add_account('81', 'Deuterium', Account_C81(inputs))
    # cost_data.add_account('82', 'Lithium-6', Account_C82(inputs))
    if application=='heat':
        cost_data.add_account('110', 'Electricity', Account_C110(inputs)) """
    
    if verbose:
        cost_data.print_summary()
    
    if save:
        cost_data.export_summary(filename='outputs-'+inputs['Run Name']+'.xlsx')
  
    # When calculating LCOE or LCOH, convert MUSD to USD first
    """ if application=='electricity':
        LCOE_result = levelized_cost(CapEx=Account_TCC(inputs)*1e6, 
                                 OperMain=Account_C70(inputs)*1e6,
                                 Fuel=Account_C80(inputs)*1e6, 
                                 Electricity_Revenue=Account_C110(inputs)*1e6,
                                 Interval=[1, inputs['Replacement Time']],
                                 Replacement=[annual_replacement_cost(inputs)*1e6, magnet_replacement_cost(inputs)*1e6],
                                 Power=inputs['Net Electric Power']*1e6,
                                 Discount=inputs['Discount'],
                                 Duration=inputs['Lifetime'],
                                 Availability=inputs['Availability'],
                                 filename='LCOE-'+inputs['Run Name']+'.csv',
                                 save=save, verbose=verbose, application='Electricity')
        
        output = pd.DataFrame(index=[0], data={'P_fusion [MW]':inputs['Fusion Power'],
                                'L_CC [m]':inputs['Central Cell Length'],
                                'P_in [MW]':inputs['Applied Heating Power'],
                                'P_net,e [MW]':inputs['Net Electric Power'],
                                'P_heat [MW]':inputs['Thermal Power'],
                                'Q_sci':inputs['Scientific Q'],
                                'Q_e':inputs['Engineering Q'],
                                'CapEx [MUSD]':Account_TCC(inputs),
                                'CapEx/Power [USD/kW]':Account_TCC(inputs)/inputs['Net Electric Power']*1e3,
                                'LCOE [USD/MWh]':LCOE_result
                                }) """

def learning_credit(p, n):
    return(p**(np.log(n)/np.log(2)))

# FOCUS ONLY ON COA 2 subaccounts
""" def magnet_replacement_cost(inputs):
    return(Account_C22_1_3(inputs))
    
def annual_replacement_cost(inputs):
    
    # Replace first wall every year - unless liquid metal is used!
    
    # End Cell
    L_magnet_to_magnet = inputs['End Plug Length'] 
 
    L_cylinder = L_magnet_to_magnet 
    
    ep = central_cell(inputs, L_cylinder)
    ep_fw_cost = 2 * ep['cost'][ep['name']=='First Wall'].values[0]/1e6

    cc = central_cell(inputs, inputs['Central Cell Length'])
    cc_fw_cost = cc['cost'][cc['name']=='First Wall'].values[0]/1e6
   
    annual_replacement_costs = cc_fw_cost + ep_fw_cost
   
    # return(0)
   
    return(annual_replacement_costs)

def Account_C10(inputs):
    # Pre-construction Costs
    return(
        Account_C11(inputs) + 
        Account_C12(inputs) + 
        Account_C13(inputs) + 
        Account_C14(inputs) + 
        Account_C15(inputs) + 
        Account_C16(inputs) + 
        Account_C17(inputs) + 
        Account_C19(inputs)        
        )
    
def Account_C11(inputs):
    # Land and Rights
    # Input MW
    # Output MUSD

    return(np.sqrt(inputs['Number of Modules']) * inputs['Neutron Power']/239 * 0.9 + inputs['Fusion Power']/239 * 0.9)

def Account_C12(inputs):
    # Site Permits
    return(10)

def Account_C13(inputs):
    # Plant Licensing
    if inputs['Licensing']:
        return(200)
    else:
        return(0)

def Account_C14(inputs):
    # Plant Permits
    return(5)

def Account_C15(inputs):
    # Plant Studies
    return(5)

def Account_C16(inputs):
    # Plant Reports
    return(2)

def Account_C17(inputs):
    # Other Pre-Construction Costs
    return(1)

def Account_C19(inputs):
    # Contingency
    if not(inputs['NOAK']) and inputs['Contingency']:
        return(0.10 * (
            Account_C11(inputs) + 
            Account_C12(inputs) + 
            Account_C13(inputs) + 
            Account_C14(inputs) + 
            Account_C15(inputs) + 
            Account_C16(inputs) + 
            Account_C17(inputs)))
    else:
        return(0) """

def Account_C20(inputs):
    return(
        Account_C21(inputs) +
        Account_C22(inputs) +
        Account_C23(inputs) +
        Account_C24(inputs) +
        Account_C25(inputs) +
        Account_C26(inputs) +
        Account_C27(inputs) +
        Account_C28(inputs) +
        Account_C29(inputs)
        )

def Account_C21(inputs):
    return(
        Account_C21_1(inputs) +
        Account_C21_2(inputs) +
        Account_C21_3(inputs) +
        Account_C21_4(inputs) +
        Account_C21_5(inputs) +
        Account_C21_6(inputs) +
        Account_C21_7(inputs) +
        Account_C21_8(inputs) +
        Account_C21_9(inputs) +
        Account_C21_10(inputs) +
        Account_C21_11(inputs) +
        Account_C21_12(inputs) +
        Account_C21_13(inputs) +
        Account_C21_14(inputs) +
        Account_C21_15(inputs) +
        Account_C21_16(inputs) +
        Account_C21_17(inputs)
        )

def Account_C21_1(inputs):
    # Site Preparation/Yard Work
    return(inputs['Gross Electric Power'] * 268/1e3)

def Account_C21_2(inputs):
    # Heat Island Building
    return(inputs['Gross Electric Power'] * 186.8/1e3)

def Account_C21_3(inputs):
    # Turbine Generator Building
    if inputs['Application'].lower()=='electricity':
        return(inputs['Gross Electric Power'] * 54.0/1e3)
    else:
        return(0)

def Account_C21_4(inputs): 
    # Heat Exchanger Building
    return(37.8/1e3 * inputs['Gross Electric Power'])

#21.05.00,,Power supply & energy storage,Concrete & Steel,9.1,9.7,9.7,6.0,560,2019,1.19,

def Account_C21_5(inputs): 
    # Power Supply and Energy Storage
    return(10.8/1e3 * inputs['Gross Electric Power'])
#21.06.00,,Reactor auxiliaries,Concrete & Steel,4.5,4.8,4.8,3.0,70,2019,1.19,

def Account_C21_6(inputs): 
    # Reactor Auxiliaries
    return(5.4/1e3 * inputs['Gross Electric Power'])

#21.07.00,,Hot cell,Concrete & Steel,65.8,24.2,24.2,60,35000,2013,1.42,

def Account_C21_7(inputs): 
    # Hot Cell
    return(93.4/1e3 * inputs['Gross Electric Power'])

#21.08.00,,Reactor services,Steel frame,13.2,4.8,4.8,10,233,2013,1.42,

def Account_C21_8(inputs): 
    # Reactor Services
    return(18.7/1e3 * inputs['Gross Electric Power'])

#21.09.00,,Service water,Steel frame,0.2,1.3,4.0,4.0,21,2019,1.19,

def Account_C21_9(inputs): 
    # Service Water
    return(0.3/1e3 * inputs['Gross Electric Power'])

#21.10.00,,Fuel storage,Steel frame,0.9,5.0,15.0,2.5,188,2019,1.19,

def Account_C21_10(inputs):
    # Fuel Storage
    return(1.1/1e3 * inputs['Gross Electric Power'])

#21.11.00,,Control room,Steel frame,0.7,4.0,12.0,2,96,2019,1.19,

def Account_C21_11(inputs):
    # Control Room
    return(0.9/1e3 * inputs['Gross Electric Power'])

#21.12.00,,Onsite AC inputs,Steel frame,0.7,3.6,10.8,1.8,70,2019,1.19,

def Account_C21_12(inputs):
    # Onsite AC Power
    return(0.8/1e3 * inputs['Gross Electric Power'])

#21.13.00,,Administration,Steel frame,3.7,20.0,60.0,10,12000,2019,1.19,

def Account_C21_13(inputs): 
    # Administration
    return(4.4/1e3 * inputs['Gross Electric Power'])

#21.14.00,,Site services,Steel frame,1.3,7.3,22.0,3.7,593,2019,1.19,

def Account_C21_14(inputs): 
    # Site Services
    return(1.6/1e3 * inputs['Gross Electric Power'])

#21.15.00,,Cryogenics,Steel frame,2.0,11.0,33.0,5.5,2003,2019,1.19,

def Account_C21_15(inputs):
    # Cyrogenics
    return(2.4/1e3 * inputs['Gross Electric Power'])

#21.16.00,,Security,Steel frame,0.7,4.0,12.0,2,96,2019,1.19,

def Account_C21_16(inputs): 
    # Security
    return(0.9/1e3 * inputs['Gross Electric Power'])

#21.17.00,,Ventilation stack,Steel cylinder & concrete foundation,22.7,,,120,,2019,1.19,

def Account_C21_17(inputs): 
    # Ventilation Stack
    return(27.0/1e3 * inputs['Gross Electric Power'])


def Account_C22(inputs):
    # Rollup
    return(
        Account_C22_1(inputs) +
        Account_C22_2(inputs) +
        Account_C22_3(inputs) +
        Account_C22_4(inputs) +
        Account_C22_5(inputs) +
        Account_C22_6(inputs) +
        Account_C22_7(inputs)
        )


def Account_C22_1(inputs):
    # This is a special case and is NOT calculated using Woodruff's model,
    # However, I maintained the naming convention for convenience
    # Rollup
    return(
        Account_C22_1_1(inputs) +
        Account_C22_1_2(inputs) +
        Account_C22_1_3(inputs) +
        Account_C22_1_4(inputs) +
        Account_C22_1_5(inputs) +
        Account_C22_1_6(inputs) +
        Account_C22_1_7(inputs) +
        Account_C22_1_8(inputs) +
        Account_C22_1_9(inputs) +
        Account_C22_1_11(inputs)
        )

def Account_C22_1_1(inputs):
    # First Wall and Blanket (and vacuum vessel)

    L_magnet_to_magnet = inputs['End Plug Length']

    L_cylinder = L_magnet_to_magnet 
    
    expander_cell_cost_result = expander_cell_cost(inputs)

    end_plug_cylindrical_part = central_cell(inputs, L_cylinder)
    end_plug_cylindrical_part_cost = end_plug_cylindrical_part['cost'].max()

    central_cell_cylindrical_part = central_cell(inputs, inputs['Central Cell Length'])
    central_cell_cylindrical_part_cost = central_cell_cylindrical_part['cost'].max()

    total_cost = central_cell_cylindrical_part_cost + 2 * end_plug_cylindrical_part_cost + 2 * expander_cell_cost_result
    
    return(total_cost/1e6)

def Account_C22_1_2(inputs):
    # Magnet Radiation Shield
    # Factor of two for each end plug
    return(2 * HF_magnet_shield_cost(inputs) / 1e6)

def Account_C22_1_3(inputs):
    # Coils
    # Rollup
    return(
        Account_C22_1_3_1(inputs) +
        Account_C22_1_3_2(inputs) +
        Account_C22_1_3_3(inputs)
        )

def Account_C22_1_3_1(inputs):
    # HF Coils - Quantity 4
    # 2 per end cell
    # 2 end cells per tandem
    return(inputs['HF Magnet Number'] * HF_magnet_cost(inputs))

def Account_C22_1_3_2(inputs):
    # LF Coils - Quantity 8
    # 4 per end cell
    # 2 end cells per tandem
    return(inputs['LF Magnet Number'] * LF_magnet_cost(inputs))

def Account_C22_1_3_3(inputs):
    # CF Coils
    # One coil every L_CF m of Central Cell
    return(inputs['CF Magnet Number'] * CF_magnet_cost(inputs))

def Account_C22_1_4(inputs):
    # Supplemenatry Heating
    # Rollup
    return(
        Account_C22_1_4_1(inputs) + 
        Account_C22_1_4_2(inputs) +
        Account_C22_1_4_3(inputs)
        )

def Account_C22_1_4_1(inputs):
    # NBI
    cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
    return(7.0642 * inputs['NBI Power'] * cost_factor)

def Account_C22_1_4_2(inputs):
    # ICRH
    cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
    return(4.149 * inputs['ICRH Power'] * cost_factor)

def Account_C22_1_4_3(inputs):
    # ECH
    cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
    return(8.0 * inputs['ECH Power'] * cost_factor)

def Account_C22_1_5(inputs):
    # Primary Structure and Support
    return(0)

def Account_C22_1_6(inputs):
    # Vacuum Systems
    # Rollup
    return(
        # Account_C22_1_6_1(inputs) + 
        Account_C22_1_6_2(inputs) +
        Account_C22_1_6_3(inputs) + 
        Account_C22_1_6_4(inputs)
        )


# def Account_C22_1_6_1(inputs):
    # Vacuum Vessel
    # Tracked in radial builds and folded into blanket
    # return(0)


def Account_C22_1_6_2(inputs):
    # Helium Liquefier-Refrigerators (not for magnets)
    # Presumably for a full vessel cryostat?
    return(0)

def Account_C22_1_6_3(inputs):

    #VACUUM PUMPING 22.1.6.3
    #assume 1 second vac rate
    #cost of 1 vacuum pump, scaled from 1985 dollars
    cost_pump = 40000
    #48 pumps needed for 200^3 system
    vpump_cap = 200/48 #m^3 capable of beign pumped by 1 pump
    no_vpumps = inputs['Vacuum Volume']/vpump_cap#Number of vacuum pumps required to pump the full vacuum in 1 second
    return(no_vpumps*cost_pump/1e6)
    

def Account_C22_1_6_4(inputs):
    # Roughing Pump
    return(120000*2.85/1e6)

def Account_C22_1_7(inputs):
    # Power Supplies

    # Not using Woodruff 2024 as that is based on ITER fusion power
    # Heating and magnets are tracked elsewhere
    
    # #Scaled relative to ITER for a 500MW fusion power syste
    # lcredit = 0.5# learning credit.
    # C220107 = 269.6 * PNRL/500*lcredit #cost in kIUA
    # C220107 = C220107*2 #assuming 1kIUA equals $2 M
    
    return(0)

def Account_C22_1_8(inputs):
    # Divertor
    return(0)

def Account_C22_1_9(inputs):
    # Direct Energy Convertor
    # Not using Woodruff 2024 numbers here, but instead Woodruff 2022
    cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
    return(1.7347 * inputs['DEC Electrical Power'] * cost_factor)

def Account_C22_1_11(inputs):
    # Assembly and Installation Costs
    
    #Cost Category 22.1.11 Installation costs
    axis_t = inputs['Overall Length']/(2*np.pi) #[m] distance from r=0 to plasma central axis - effectively major radius
    axis_ir = axis_t

    # Define labor rate
    lr = 1600 / 1e6  # 1600 dollars per day for skilled labor

    # Calculations
    constructionworker = 20 * axis_ir / 4
    C_22_1_11_in = inputs['Number of Modules'] * inputs['Construction Time'] * (lr * 20 * 300)
    C_22_1_11_1_in = inputs['Number of Modules'] * ((lr * 200 * constructionworker) + 0)  # 22.1 first wall blanket
    C_22_1_11_2_in = inputs['Number of Modules'] * ((lr * 150 * constructionworker) + 0)  # 22.2 shield
    C_22_1_11_3_in = inputs['Number of Modules'] * ((lr * 100 * constructionworker) + 0)  # coils
    C_22_1_11_4_in = inputs['Number of Modules'] * ((lr *  30 * constructionworker) + 0)  # supplementary heating
    C_22_1_11_5_in = inputs['Number of Modules'] * ((lr *  60 * constructionworker) + 0)  # primary structure
    C_22_1_11_6_in = inputs['Number of Modules'] * ((lr * 200 * constructionworker) + 0)  # vacuum system
    C_22_1_11_7_in = inputs['Number of Modules'] * ((lr * 400 * constructionworker) + 0)  # power supplies
    C_22_1_11_8_in = 0  # guns or divertor
    C_22_1_11_9_in = inputs['Number of Modules'] * ((lr * 200 * constructionworker) + 0)   # direct energy converter
    C_22_1_11_10_in = 0  # ECRH

    # Total cost calculations
    C220111 = (C_22_1_11_in + C_22_1_11_1_in + C_22_1_11_2_in + C_22_1_11_3_in + C_22_1_11_4_in + C_22_1_11_5_in + C_22_1_11_6_in + C_22_1_11_7_in + C_22_1_11_8_in + C_22_1_11_9_in + C_22_1_11_10_in)

    cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
    
    return(C220111 * cost_factor)

def Account_C22_2(inputs):
    # Main and Secondary Coolant
    return(
        Account_C22_2_1(inputs) +
        Account_C22_2_2(inputs) +
        Account_C22_2_3(inputs)
        )

def Account_C22_2_1(inputs):
    # Primary Coolant
    return(166  * (inputs['Number of Modules'] * inputs['Gross Electric Power']/1000))

def Account_C22_2_2(inputs):
    # Secondary Coolant
    return(40.6 * (inputs['Thermal Power']/3500)**0.55)

def Account_C22_2_3(inputs):
    # Tertiary Coolant
    return(0)

def Account_C22_3(inputs):
    # Auxiliary Cooling Systems
    return(1.10 * 1e-3 * inputs['Number of Modules'] * inputs['Thermal Power'] * 2.02)

def Account_C22_4(inputs):
    # Radioactive Waste Treatment
    return(1.96 * 1e-3 * inputs['Thermal Power'] * 2.02)

def Account_C22_5(inputs):
    # Cost Category 22.5 Fuel Handling and Storage

    inflation = 1.43
    C2205010ITER = 20.465 * inflation
    C2205020ITER = 7 * inflation
    C2205030ITER = 22.511 * inflation
    C2205040ITER = 9.76 * inflation
    C2205050ITER = 22.826 * inflation
    C2205060ITER = 47.542 * inflation
    # C22050ITER = C2205010ITER + C2205020ITER + C2205030ITER + C2205040ITER + C2205050ITER + C2205060ITER #ITER inflation cost


    lcredit = 0.8 # learning curve
    ltoak = 10**(np.log10(lcredit) / np.log10(2))


    C220501 = C2205010ITER * ltoak
    C220502 = C2205020ITER * ltoak
    C220503 = C2205030ITER * ltoak
    C220504 = C2205040ITER * ltoak
    C220505 = C2205050ITER * ltoak
    C220506 = C2205060ITER * ltoak
    C220500 = C220501 + C220502 + C220503 + C220504 + C220505 + C220506 #ITER inflation cost
    
    cost_factor = (0.80)**(np.log(inputs['Unit Number'])/np.log(2))
    
    return(C220500 * cost_factor)

def Account_C22_6(inputs):
    # Cost Category 22.6 Other Reactor Plant Equipment
    return(11.5*(np.max((inputs['Net Electric Power'],0))/1000)**(0.8))

def Account_C22_7(inputs):
    # Cost Category 22.7 Instrumentation and Control
    return(85)

def Account_C23(inputs):
    # Turbine Plant Equipment
    return(inputs['Number of Modules'] * inputs['Gross Electric Power'] * 0.219 *1.15)

def Account_C24(inputs):
    # Electric Plant Equipment
    return(inputs['Number of Modules'] * inputs['Gross Electric Power'] * 0.054 * 1.15)

def Account_C25(inputs):
    # Miscellaneous Plant Equipment
    return(inputs['Number of Modules'] * inputs['Gross Electric Power']  * 0.038 * 1.15)
  
def Account_C26(inputs):
    # Heat Rejection
    return(inputs['Number of Modules'] * inputs['Net Electric Power'] * 0.107 * 1.15 )

def Account_C27(inputs):
    # Special Materials
    # Total elsewhere, implement later
    return(0)

def Account_C28(inputs):
    # Digital Twin
    return(5)

def Account_C29(inputs):
    # Contingency on Direct Capital Costs
    
    # I may have to change the way that I do sums as this must be done separately?
    # C21 = sum(C21.1 + C21.2 + ...)

    # Rollup
    
    if not(inputs['NOAK']) and inputs['Contingency']:
        return(0.1 * (
            Account_C21(inputs) + 
            Account_C22(inputs) + 
            Account_C23(inputs) + 
            Account_C24(inputs) + 
            Account_C25(inputs) + 
            Account_C26(inputs) + 
            Account_C27(inputs) +
            Account_C28(inputs)))
    else:
        return(0)


""" def Account_C30(inputs):
    # Rollup
    return(
        Account_C31(inputs) + 
        Account_C32(inputs) + 
        Account_C33(inputs) + 
        Account_C34(inputs) + 
        Account_C35(inputs) + 
        Account_C36(inputs) + 
        Account_C37(inputs) + 
        Account_C38(inputs) + 
        Account_C39(inputs)
        )
#Cost Category 31 – Field Indirect Costs - previously Cost Category 93


def Account_C31_LSA(inputs):
    # Indirect Cost Factors for different LSA levels
    fac_93 = [0.0520, 0.0600, 0.0640, 0.0870]  # x TDC [90] 
    return(fac_93[inputs['Level of Safety Assurance'] - 1] * Account_C20(inputs))
	
	
#0.060 * C_90; %NMOD*(/1e6)/A_power * A_C_93 #Field Office Engineering and Services  Table 3.2-VII of Ref. [1]

def Account_C31(inputs):
    if inputs['Net Electric Power'] > 0:
        return( (np.max((inputs['Net Electric Power']/150,0)))**-0.5 * inputs['Net Electric Power'] * 0.02 * inputs['Construction Time'])
    else:
        return(0)

#Cost Category 32  – Construction Supervision - previously Cost Category 91

def Account_C32_LSA(inputs):
    fac_91 = [0.1130, 0.1200, 0.1280, 0.1510]  # x TDC [90]
    return( fac_91[inputs['Level of Safety Assurance'] - 1] * Account_C20(inputs))

def Account_C32(inputs): 
    if inputs['Net Electric Power'] > 0:

        return( (inputs['Net Electric Power']/150)**-0.5 * inputs['Net Electric Power'] * 0.05 * inputs['Construction Time']) #this takes the 316$/kW and divides by 6 to obtain a cost per year of 0.053$/MW and applies to PE, which is the net electric.  There are arguments that this should be applied to the gross electric, if we consider demonstration plants, but this code is not set up for FOAK currently.

    else:
        return(0)

def Account_C33(inputs):
    #Cost Category 33 – Commissioning and Start-up Costs
    return(0)

def Account_C34(inputs):
    #Cost Category 34 – Demonstration Test Run
    return(0)

def Account_C35(inputs): 
    #Cost Category 35 – Design Services Offsite
    cost_factor = (0.70)**(np.log(inputs['Unit Number'])/np.log(2))

    if inputs['Net Electric Power'] > 0:
        return( (inputs['Net Electric Power']/150)**-0.5 * inputs['Net Electric Power'] * 0.03 * inputs['Construction Time'] * cost_factor)
    else:
        return(0)

def Account_C35_LSA(inputs):
    fac_92 = [0.0520, 0.0520, 0.0520, 0.0520]  # x TDC [90]
    return( fac_92[inputs['Level of Safety Assurance'] - 1] * Account_C20(inputs))
#0.052 * C_90; %NMOD*(/1e6)/A_power * A_C_92; %Home Office Engineering and Services  Table 3.2-VII of Ref. [1]

def Account_C36(inputs):
    # PM/CM Services Offsite
    return(0)

def Account_C37(inputs):
    # Design Servies Offsite
    return(0)

def Account_C38(inputs):
    # PM/CM Services Onsite
    return(0)

def Account_C39(inputs):
    # Contingency on Support Services
    if not(inputs['NOAK']) and inputs['Contingency']:
        return(0)
    else:
        return(0)







#Cost Category 40 Capitalized Owner’s Cost (COC)

def Account_C40_LSA(inputs):
    fac_91 = [0.1130, 0.1200, 0.1280, 0.1510]  # x TDC [90]
    return( fac_91[inputs['Level of Safety Assurance'] - 1] * Account_C20(inputs))

def Account_C40(inputs): 
    return(Account_C40_LSA(inputs))
#Cost Category 41 – Staff Recruitment and Training

def Account_C41(inputs):
    return(0)

#Cost Category 42 – Staff Housing

def Account_C42(inputs):
    return(0)

#Cost Category 43 – Staff Salary-Related Costs

def Account_C43(inputs): 
    return(0)

#Cost Category 44 – Other Owner’s Costs

def Account_C44(inputs): 
    return(0)

def Account_C49(inputs): 
    # Contingency on Owner's Costs
    if not(inputs['NOAK']) and inputs['Contingency']:
        return(0)
    else:
        return(0)


#Cost Category 50 Capitalized Supplementary Costs (CSC)


#Cost Category 51 – Shipping and Transportation Costs

def Account_C51(inputs): 
    return(8)

#Cost Category 52 – Spare Parts

def Account_C52(inputs): 
    return(0.1 * (
        Account_C23(inputs) + 
        Account_C24(inputs) + 
        Account_C25(inputs) + 
        Account_C26(inputs) + 
        Account_C27(inputs) + 
        Account_C28(inputs)))

#Cost Category 53 – Taxes

def Account_C53(inputs):
    if inputs['Tax']:
        return(100)
    else:
        return(0)

#Cost Category 54 – Insurance

def Account_C54(inputs): 
    return(1)

#Cost Category 55 – Initial Fuel Load



def Account_C55(inputs): 
    return(inputs['Net Electric Power']/150 * 34)

#Cost Category 58 – Decommissioning Costs

def Account_C58(inputs): 
    if inputs['Decommissioning']:
        return(200)
    else:
        return(0)

#Cost Category 59 – Contingency on Supplementary Costs

def Account_C59(inputs):
    
    # For the future, the sum of C59 should just be calculated as sum of (C51:C59) * NOAK_factor
    # Similarly for C29...
    if not(inputs['NOAK']) and inputs['Contingency']:
        return(0.1 * (
            Account_C51(inputs) +
            Account_C52(inputs) +
            Account_C53(inputs) +
            Account_C54(inputs) + 
            Account_C55(inputs) + 
            Account_C58(inputs)
            ))
    else:
        return(0)

def Account_C50(inputs):
    return(
        Account_C51(inputs) +
        Account_C52(inputs) +
        Account_C53(inputs) +
        Account_C54(inputs) + 
        Account_C55(inputs) + 
        Account_C58(inputs) +
        Account_C59(inputs)
        )

def Account_C60(inputs):
    #Cost Category 60 Capitalized Financial Costs (CFC)
    return(
        Account_C61(inputs) +
        Account_C63(inputs)
        )

def Account_C61(inputs):
    #Cost Category 61 – Escalation - formerly Cost Category 98: Escalation During Construction
    A_C_98 = 115
    A_power = 1000
    
    if inputs['NOAK']:
        learning_credit = 0.00
    else:
        learning_credit = 1.00
    
    return(inputs['Number of Modules']*inputs['Fusion Power']/A_power * A_C_98 * learning_credit) #Escalation during Construction (EDC) Table 3.2-X of Ref. [1]

def Account_C62(inputs):
    # Fees
    return(0)

def Account_C63(inputs):
    # Cost Category 63 – Interest During Construction (IDC) formerly cost category 97
    
    # return(inputs['Net Electric Power'] * 0.099 * inputs['Construction Time'])

    # Woodruff uses a weird formula.  Why not use an analytic formula that's 100% correct for any discount rate?
    
    # Champlin Thesis Equation 4a
    r = inputs['Discount']
    T = inputs['Construction Time']
    IDCM = ((1+r)**(1+T) - (1+r))/(r*T) 
    
    Overnight_Cost = Account_OCC(inputs)
    
    IDC = (IDCM-1) * Overnight_Cost
    
    return(IDC)

    
def Account_C63_LSA(inputs):
    # Cost Category 63 – Interest During Construction (IDC) formerly cost category 97

    fac_97 = [0.2651, 0.2736, 0.2787, 0.2915]  # applied only to C90, x TDC [90+91+92+93+94+95+96]

    return(fac_97[inputs['Level of Safety Assurance'] - 1] * Account_C20(inputs))


def Account_C69(inputs):
    # Contingency on Capitalized Financial Costs
    if not(inputs['NOAK']) and inputs['Contingency']:
        return(0)
    else:
        return(0) """

def Account_OCC(inputs):
    # Overnight Capital Cost
    return Account_C20(inputs)
    """ return(
        Account_C10(inputs) +
        Account_C20(inputs) +
        Account_C30(inputs) +
        Account_C40(inputs) +
        Account_C50(inputs)
        ) """


def Account_TCC(inputs):
    # Total Capital Cost
    return Account_C20(inputs)
    """return(
        Account_C10(inputs) +
        Account_C20(inputs) +
        Account_C30(inputs) +
        Account_C40(inputs) +
        Account_C50(inputs) +
        Account_C60(inputs)
        ) """

""" def Account_C70(inputs):
    # Annualized O&M Cost (AOC)
    # Output is MUSD/year
    
    return(60 * inputs['Net Electric Power'] * 1000 / 1e6)

def Account_C80(inputs):
    # Cost Category 80: Annualized Fuel (and electricity) Cost (AFC)
    # Output is MUSD/year
    return(
        Account_C81(inputs) +
        Account_C82(inputs)
        )
    
def Account_C81(inputs):
    # Deuterium Cost in MUSD/year
    # M_D = 2.014 # amu
    # m_D = 3.342e-27 # kg
    p_D = 8040 #Where u_D ($/kg) = 2175 ($/kg) from STARFIRE 1980, which is a CPI-U ratio of 304.702 / 82.4
    # STARFIRE References the 1979 report https://www.osti.gov/servlets/purl/5532719 which gives $2,000/kg on page 90 
    # C_F = inputs['Number of Modules'] * inputs['Fusion Power'] * 1e6 * 3600 * 8760 * p_D * m_D * inputs['Availability'] / (17.58 * 1.6021e-13)
    burn_rate = m_D * 60 * 60 * 8760 / E_DT * 1e6 # kg/MW/year
    C_F = inputs['Number of Modules'] * inputs['Fusion Power'] * inputs['Availability'] * burn_rate * p_D

 
    return(C_F/1e6)

def Account_C82(inputs):
    # Return lithium-6 cost in MUSD/year

    p_6Li = 3500 # Estimated from El Guebaly 2011 ($2,400/kg for 90%) adjusted for inflation
    C_F = inputs['Number of Modules'] * inputs['Fusion Power'] * 1e6 * 3600 * 8760 * p_6Li * m_6Li * inputs['Availability'] / E_DT
    
    return(C_F/1e6)

def Account_C110(inputs):
    # Annual electricity cost (Revenue if negative) in MUSD/year
    # Only include for process heat
    
    if inputs['Application'].lower() == 'heat' and inputs['Method']=='new':
    
        p_elec = 100 # USD/MWh 
        p_elec = 40 # USD/MWh - https://enerknol.com/average-2024-u-s-wholesale-electricity-prices-projected-to-be-similar-to-2023-levels-eia/
        p_elec = 77 # USD/MWh
        C = - inputs['Net Electric Power'] * inputs['Availability'] * 8760 * p_elec
        
        return(C/1e6)
    
    else:
        
        return(0)
    
    pass """

def Account_C90(inputs):
    # Cost Category 90: Annualized Financial Costs (AFC)
    f_cr = 0.09   #Capital return factor
    return(f_cr * Account_TCC(inputs))


def PbLi_density(f_6Li=0.075, T=300):
    """
    Returns PbLi density [kg/m^3]. Assumes the PbLi is a eutectic, which has
    roughly 83% Pb and 17% Li.

    Parameters
    ----------
    f_6Li : float, optional
        Fraction of 6Li to all Li, aka enrichment. The default is 0.075.
    T : float, optional
        Temperature. Units are °C. The default is 300.

    Returns
    -------
    Density of PbLi at selected parameters.

    """
    
    f_6Li_natural = 0.075
    rho_6Li = 0.460e3 # kg/m^3
    rho_7Li = 0.537e3 # kg/m^3

    T_K = T + 273.15 # K

    # Use equation for density as function of temperature from below, Table 1
    # Note this is valid only from 508 K to 880 K (234.85 °C to 606.85 °C)
    # https://pubs.aip.org/aip/jcp/article-abstract/27/5/1033/204623/Bulk-Density-of-Separated-Lithium-Isotopes?redirectedFrom=PDF
    rho_PbLi = 10520.35 - 1.19051 * T_K
    
    
    # Correct calculated density for enrichment
    rho_PbLi = rho_PbLi * (rho_6Li * f_6Li + rho_7Li * (1-f_6Li)) / (rho_6Li * f_6Li_natural + rho_7Li * (1-f_6Li_natural))
    
    return(rho_PbLi)

def Li_price(f_6Li=0.075):
    """
    Return Li price (USD/kg) for enrichment levels above 90% 6Li

    Parameters
    ----------
    f_6Li : TYPE, optional
        DESCRIPTION. The default is 0.075.

    Returns
    -------
    None.

    """
    
    # https://www.dailymetalprice.com/lithium.html
    # From 2024-04-01
    P_6Li075 = 15.152 # USD/kg
    
    if f_6Li == 0.075:
        return(P_6Li075)
    
    elif f_6Li >= 0.90:
        # From Woodruff for 90% 6Li
        P_6Li90 = 70 # USD/kg
        
        # El-Guebaly 2011 (AIRES-AT UK Study)
        # P_6Li90 = 2400.0 #USD/kg
        
        
        f = [0.90, 0.99, 0.999, 0.9999, 0.99999]
        Cf = [1, 2, 4, 8, 16]
        
        f_interp = scipy.interpolate.interp1d(f, Cf)
        return(f_interp(f_6Li) * P_6Li90)
    
    else:
        print('Lithium pricing at this enrichment level not supported')
        return()

def PbLi_price(f_6Li, P_Pb):
    
    # Assuming eutectic fractions
    f_Li = 0.17
    f_Pb = 1 - f_Li

    P_Li = Li_price(f_6Li)
    
    P_PbLi = f_Pb * P_Pb + f_Li * P_Li # USD/kg
    
    return(P_PbLi)

def V_cylindrical_shell(r_in, r_out, L):
    """
    Return volume of a cylindrical shell

    Parameters
    ----------
    r_in : float, inner radius
    r_out : float, outer radius
    L : float, length

    Returns
    -------
    Volume (float).

    """
    return(np.pi * L * (r_out**2 - r_in**2))
    
def V_inverse_triangular_washer(z, r_in, r_out):
    """
    Return volume of cylindrical inverse triangular washer.
    From the ASCII art below you can see how this is used for magnet shielding.
    
                  ^ z
                  |
                  |               z
    |\            |            /|
    | \           |           / |
    |  \          |          /  |
    |   \         |         /   |   
    |    \        |        /    |
    |     \       |       /     |
    ------------------------------------> r
                          r_in  r_out 

    Parameters
    ----------
    z : float, z extent of triangle
    r_in : float, inner radius of triangle
    r_out : float, outer radius of triangle

    Returns
    -------
    Volume (float).

    """
    
    
    # https://www.wolframalpha.com/input?i=integral+of+2+pi+r+%28+z*r+%2F+%28b-a%29++-+z*a+%2F+%28b-a%29+%29+dr+from+a+to+b
    
    return(np.pi * z / 3 * (r_out - r_in) * (r_in + 2 * r_out))

def generate_inputs(
        
    application='heat',
  
    P_f=1, P_f_L=1, P_f_EP=1,
    P_NBI=1, P_ECH=1, P_ICRH=1,
    M_n=1.1, 
    
    N_module=1, 
    
    f_pump=0.03, f_sub=0.04, f_cryo=0.01,   
    
    # Obsolete but kept for backwards compatibility
    P_pump=1, P_sub_cont=1, P_cryo=1, 
    P_pfcool=0, P_thcool=0, P_coils=0, P_aux=1,
    
    eta_th=0.50, eta_DEC=0.90, eta_pump=0.98, 
    eta_NBI=0.50, eta_ECH=0.50, eta_ICRH=0.50,
    
    verbose=False, exact=False, 
    NOAK=False, n_unit=False,
    construction_time=6,
    lifetime=30, replacement=10, availability=0.90, 
    discount=0.0245,
    LSA=2, 
    cost_file='woodruff-data.csv', method='new',
    include_decommissioning=False, include_tax=False,
    include_licensing=False, include_contingency=False,
    
    hf_magnet_length=1,
    hf_magnet_shielding_thickness=1,
    
    a_EC=1,
    expander_cell_vessel_thickness=0.01,
    expander_cell_vessel_material='SS316',
    
    vacuum_gap_CC=0.01,
    first_wall_material='W',
    first_wall_thickness=0.01,
    vacuum_vessel_material='SS316',
    vacuum_vessel_thickness=0.01,
    multiplier_material='Pb',
    multiplier_thickness=0.01,
    blanket_coolant_material='Natural PbLi',
    blanket_thickness=1.00,
    blanket_coolant_fraction=0.90,
    blanket_structural_material='SS316',
    blanket_structural_fraction=0.10,
    outer_vessel_thickness=0.01,
    
    L_EP=1,
    L_EC=1,  
    a_CC=1,
    a_EP=1,
   
    save=True,
    load=False,
    filename=None,
    run_name=None
   
    ):
    
    """
    Return a dict containing all inputs for a techno-economic analysis.
    
    Parameters
    ----------
    application : str, optional
        The application, either 'electricity' or 'heat'. 
        This changes the power balance and some reporting. The default 
        is 'heat'.
    P_f : float
        The total fusion power in MW.  The length of the central cell 
        is scaled to achieve this value. This is not the net electrical power!
    P_f_L : float
        The central cell linear fusion power in MW/m. 
    P_f_EP : float
        The fusion power in each of two end plugs in MW.  
    P_NBI : float 
        The applied NBI power in MW.  
    P_ECH : float
        The applied ECH power in MW.  
    P_ICRH : float
        The applied ICRH power in MW.  
    M_n : float
        The neutron power multiplication factor from the blanket.  
        The default is 1.1.
    N_module : int
        The number of modules (fusion machines) per facility.  
        This is deprecated. The default is 1. 
    f_pump : float
        The pumping power fraction (of M_n * P_fusion).  The default is 0.03.
    f_sub : float
        The subsystem power fraction (of fusion power).  The default is 0.04.
    f_cryo : float
        The cryogenic power fraction (of fusion power).  The default is 0.01.
    P_pump : float
        The pumping power in MW.  This is deprecated.
    P_sub_cont : float
        The subsystem and control power in MW.  This is deprecated.
    P_cryo: float
        The cryo power in MW.  The default is 0.5 MW.  This is deprecated.
    P_pfcool : float
        The PF cooling power in MW.  The default is 0.  This is deprecated. 
    P_thcool : float
        The thermal cooling power in MW.  The default is 0.  This is deprecated.
    P_coils : float
        The magnetic coil power in MW.  The default is 0.
    P_aux : float
        The auxiliary power in MW.  The default is 9.4. 
        
    eta_th : float
        The thermal conversion efficiency.  
    eta_DEC : float
        The DEC conversion efficiency.  The default is 0.90.
    eta_pump : float
        The pumping efficiency.  The default is 0.98.
    eta_NBI : float
        The NBI electrical efficiency.  
    eta_ECH : float
        The ECH electrical efficiency.  
    eta_ICRH : float
        The ICRH electrical efficiency.  
    
    LSA : int
        The level of safey assurance.  The default is 2.  This is deprecated.
        
    construction_time : int
        The construction time in years.  The default is 6.
    NOAK : bool
        Whether this is an NOAK device.  The default is False.  
        This will probably be deprecated soon.
    n_unit : int or bool
        The number of the tandem unit, in terms of first of a kind (1), 
        second of a kind (2), etc.  When this is False, the FOAK cost is used.
        The default is False.
    lifetime : int 
        The lifetime of the tandem in years.  This is used for LCOE and LCOH 
        calcualtions.  The default is 30.
    replacement : int 
        The replacement interval of the magnets in years.  The default is 10.
    availability : float
        The facility availability. The range is between 0 and 1, inclusive.
        The default is 0.90.
    cost_file : str
        The filename of the cost file.  The default is 'woodruff-data.csv'.
    method : str
        The power balance method.  The default is 'new'.  
        This will be deprecated soon.
    include_tax : bool
        Whether to include tax.  The default is False.
    include_decommissioning : bool
        Whether to include decommissioning.  The default is False.
    include_licensing : bool
        Whether to include licensing.  The default is False.
    include_contingency : bool
        Whether to include continency.  The default is False.
    verbose : bool
        Whether to print a lot.  The default is False.
    vacuum_gap_CC : float
        The vacuum gap in the central cell, in meters.  The default is 0.01.
    first_wall_material : str
        The first wall material.  The default is 'W'.
    first_wall_thickness : float
        The first wall thickness, in meters.  The default is 0.01.
    vacuum_vessel_material : str
        The vacuum vessel material.  The default is 'SS316'.
    vacuum_vessel_thickness : float
        The vacuum vessel thickness, in meters.  The default is 0.01
    multiplier_material : str
        The muliplier material.  The default is 'Pb'
    multiplier_thickness : float
        The multiplier thickness, in meters.  The default is 0.01.
    blanket_coolant_material : str
        The blanket coolant material.  The default is 'Natural PbLi'.
    blanket_thickness : float
        The blanket thickness, in meters.  The default is 1.00.
    blanket_coolant_fraction : float
        The blanket coolant fraction, from 0 to 1.  The default is 0.90.
    blanket_structural_material : str
        The blanket structural material.  The default is 'SS316'.
    blanket_structural_fraction : float
        The blanket structural fraction, from 0 to 1.  The default is 0.10.
    outer_vessel_thickness : float
        The outer vessel thickness, in meters.  The default is 0.01.
    contours : bool
        Whether to plot contours of discount rates and build time. 
        The default is False.
    tornadoes : bool
        Whether to plot tornado plots.  These take a while to make.  
        The default is False.
 
    hf_magnet_length : float
        The axial length of the HF magnet, in meters.  The default is 1.0.
    hf_magnet_shielding_thickness : 
        The default is 1.0,
    
    a_EC : float
        The expander cell radius, in meters.  The default is 1.0.
    expander_cell_vessel_thickness : float
        The expander cell vessel thickness, in meters.  The default is 0.01.
    expander_cell_vessel_material : str
        The expander cell vessel material.  The default is 'SS316'.
    

    
    L_EP : float
        The length of each end plug, in meters.  The default is 1.
    L_EC : float
        The length of each expander cell, in meters, measured from the 
        centers of the HF coils.  The default is 1.  
    a_CC : float
        The central cell plasma radius, in meters.  The default is 15.
    a_EP : float
        The end plug plasma radius, in meters.  The default is 1.



    
    save : bool
        Whether to save the results.  The default is True.
    load : bool
        Whether to load results.  The default is False.
    filename : str
        The filename loading.  The default is None.
    run_name : str
        A run name for saving results.  The default is None.
    
    
    """
                
    if load:
        with open(filename) as file:
            inputs = json.load(file)
            
    else:
        
        # Fusion Power in Central Cell    
        P_f_CC = P_f - 2 * P_f_EP
        
        # Central Cell Length
        L_CC = P_f_CC/P_f_L
        
        # Central Field Coil Spacing
        L_CF = 1.0
    
        # Overall Device Length
        L = L_CC + 2 * L_EP + 2 * L_EC
        
        # Vacuum Volume - Not precise, but also not important
        # Should be updated
        V_vac = L * np.pi * a_EC**2
    
    
        # Power Balance
        P_alpha = P_f * E_alpha / E_DT  # MW, alpha power
        P_n = P_f - P_alpha # MW, neutron power
            
        # Input electrical power
        P_ine = P_NBI/eta_NBI + P_ICRH/eta_ICRH + P_ECH/eta_ECH

        # Balance of Plant
        P_pump = f_pump * M_n * P_n
        P_sub_cont = f_sub * P_f
        P_cryo = f_cryo * P_f
        P_other = P_pump + P_sub_cont + P_cryo

        # Total heating input power applied to plasma
        P_in = P_NBI + P_ICRH + P_ECH

        # Heat in blanket including neutron multiplication
        # P_thermal_only = M_n * P_n
        
        # Thermal power
        # No P_in term as that goes to DEC
        P_th = M_n * P_n +  eta_pump * P_pump 
        
        # Thermal electric power
        P_the = eta_th * P_th
        
        # DEC receives all charged particle exhaust, so is the sum of 
        # both the input power and alpha power
        P_DEC = P_in + P_alpha
        
        # DEC electrical power
        P_DECe = eta_DEC * P_DEC
        
        # Gross electrical power
        # Differs for application
        if application.lower()=='electricity':
            # Electrical application uses thermal power to create electricity
            P_egross = P_DECe + P_the
        elif application.lower()=='heat':
            # Heat application only uses DEC to create electricity
            P_egross = P_DECe

        # Net electrical power
        P_enet = P_egross - (P_ine + P_other)
            
        f_aux =  P_aux / P_egross
        # P_loss = P_th - P_the - P_DECe
        # P_sub = f_sub * P_the
        
        # Scientific Q
        Q_sci = P_f / P_in
        
        # Engineering Q
        Q_eng = P_egross / (P_ine + P_other)

        # Recirculating power
        f_refrac = 1 / Q_eng
        if run_name==None:
            run_name = '{:.1f}-MW'.format(float(P_f))
        

        cost_file_full = pkg_resources.resource_filename('TEAm_public', cost_file)
               
        inputs = {
            
            # Application (heat or electricity)
            'Application':application,
            'Method':method,
            
            # Power Balance
            'Fusion Power': P_f, 
            'Alpha Power': P_alpha, 
            'Neutron Power': P_n, 
            'Neutron Energy Multiplication': M_n, 
            # 'Thermal Only Power': P_thermal_only,
            'Thermal Power': P_th, 
            'Thermal Conversion Efficiency': eta_th, 
            
            # DEC
            'DEC Efficiency': eta_DEC, 
            'DEC Electrical Power': P_DECe, 
            'DEC Input Power': P_DEC, 
            
            # Balance
            'Thermal Electric Power': P_the, 
            'Gross Electric Power': P_egross, 
            'Net Electric Power': P_enet,
            
            # Other Power
            'Other Power': P_other,
            'Pumping Power Fraction': f_pump, 
            'Pumping Power': P_pump, 
            'Subsystem and Control Power': P_sub_cont, 
            'Auxiliary Power Fraction': f_aux, 
            'Auxiliary Power': P_aux, 
            
            # Input Power
            'Applied Heating Power': P_in, 
            'Applied Heating Power Electrical Use': P_ine,
            'NBI Power': P_NBI,
            'ICRH Power': P_ICRH,
            'ECH Power': P_ECH,
            'NBI Electrical Efficiency': eta_NBI,
            'ICRH Electrical Efficiency': eta_ICRH,
            'ECH Electrical Efficiency': eta_ECH,
            
            # Q
            'Scientific Q': Q_sci, 
            'Engineering Q': Q_eng, 
            'Recirculating Power Fraction': f_refrac, 

            # Don't use this - it is probably not implemented well here
            'Number of Modules': N_module,
            
            # Time Intervals
            'Construction Time':construction_time,
            'Lifetime':lifetime,
            'Replacement Time':replacement,
            'Level of Safety Assurance':LSA,
            
            # Geometry
            'Overall Length':L,
            'Central Cell Length':L_CC,
            'End Plug Length':L_EP,
            'Expander Length':L_EC,
            'Vacuum Volume':V_vac,
            
            # Number of Magnets
            'HF Magnet Number':4, # Always 4 for a tandem
            'LF Magnet Number':2, # Set to what you need!
            'CF Magnet Spacing':L_CF,
            'CF Magnet Number':L_CC/L_CF, # Calcuated
            
            'HF Magnet Length':hf_magnet_length,
            'HF Magnet Shielding Thickness':hf_magnet_shielding_thickness,
            
            'End Plug Plasma Radius':a_EP,
            
            'Expander Cell Length':L_EC,
            'Expander Cell Radius':a_EC,
            'Expander Cell Vessel Thickness':expander_cell_vessel_thickness,
            'Expander Cell Vessel Material':expander_cell_vessel_material,
            
            'Central Cell Plasma Radius':a_CC,
            'Central Cell Vacuum Gap':vacuum_gap_CC,
            'First Wall Material':first_wall_material,
            'First Wall Thickness':first_wall_thickness,
            'Vacuum Vessel Material':vacuum_vessel_material,
            'Vacuum Vessel Thickness':vacuum_vessel_thickness,
            'Multiplier Material':multiplier_material,
            'Multiplier Thicnkess':multiplier_thickness,
            'Blanket Coolant Material':blanket_coolant_material,
            'Blanket Thickness':blanket_thickness,
            'Blanket Coolant Fraction':blanket_coolant_fraction,
            'Blanket Structural Material':blanket_structural_material,
            'Blanket Structrual Fraction':blanket_structural_fraction,
            'Outer Vessel Thickness':outer_vessel_thickness,
    
            # Economic Factors
            'Availability':availability,
            'Discount':discount,
            'NOAK': NOAK,
            'Unit Number':n_unit,
            # 'Cost File':cost_file,
            'Cost File':cost_file_full,
            'Licensing':include_licensing,
            'Tax':include_tax,
            'Decommissioning':include_decommissioning,
            'Contingency':include_contingency,

            # File Prefix
            'Run Name':run_name
            
            }
        
        if save:
            # import csv
            
            filename = 'inputs-'+inputs['Run Name']+'.json'    

    
            with open(filename, 'w') as file:
                json.dump(inputs, file)

    if verbose:
        
        format_string = '{:35s} {:8.2f}'
        
        print('{:35s} {:8s}'.format('Parameter', 'Value'))
        
        for key in inputs:
            print(format_string.format(key, inputs[key]))
        
    return(inputs)


""" def levelized_cost(CapEx=1e6, 
        OperMain=1e6, 
        Fuel=1e6, 
        Electricity_Revenue=1e6,
        Replacement=[1e6, 1e6], Interval=[1, 10], 
        Power=1e6, 
        Availability=0.90, 
        Discount=0.0245, 
        Duration=30,
        verbose=True,
        save=True,
        filename=None,
        application='Electricity'):
    """
"""

    Parameters
    ----------
    CapEx : float, optional
        Capital expense [USD]. 
    OperMain : float, optional
        Annual operations and maintenance costs [USD]. 
    Fuel : float, optional
        Annual fuel costs [USD]. 
    Electricity Revenue : float, optional
        Annual revenue from selling electricity (for process heat applications only).  
    Replacement : array of floats, optional
        Every n year replacement costs in an array. 
    Interval : array of ints, optional
        Number of years between replacements in an array. The default is [1, 10].
    Power : float, optional
        Output power [W]. Use net electric power for LCOE and heat output for LCOH. 
    Availability : float, optional
        Plant annual availability (between 0 and 1). The default is 0.90.
    Discount : float, optional
        Discount rate. The default is 0.0245.
    Duration : int, optional
        Lifetime of plant [year]. The default is 30.
    verbose : bool, optional
        Flag for more detailed output. The default is True.
    save : bool, optional
        Flag for saving outputs. The default is True.

    Returns
    -------
    Levelized cost, either or electricity or of heat, depending on the 
    application.  For electricity, the units are USD/MWh, and for heat, the
    units are USD/MMBTU.
    """

"""
    
    # Set up DataFrame for annual values
    data = pd.DataFrame(data={'Year':range(1,Duration+1),
                              'Power':Power*np.ones(Duration),
                              'Investment':np.zeros(Duration),
                              'Replacement':np.zeros(Duration),
                              'O&M':OperMain*np.ones(Duration),
                              'Electricity Revenue':Electricity_Revenue*np.ones(Duration),
                              'Fuel':Fuel*np.ones(Duration)
                              })
    
    data.loc[0, 'Investment'] = CapEx
    
    for i, r in zip(Interval, Replacement):
        data.loc[0::int(i), 'Replacement'] += r
        data.loc[0, 'Replacement'] = 0

    # Here power is in MW
    data['Denominator'] = ((data['Power']/1e6 * Availability * 8760)/(1+Discount)**(data['Year'])).cumsum() # MWh/year

    data['Numerator'] = ((data['Investment'] + 
                             data['Replacement'] +
                             data['O&M'] +
                             data['Fuel'] +
                             data['Electricity Revenue']) / (1+Discount)**(data['Year'])).cumsum()        


    data['CapEx Contribution']       = (data['Investment']          / (1+Discount)**(data['Year'])).cumsum() / data['Denominator']
    data['Replacement Contribution'] = (data['Replacement']         / (1+Discount)**(data['Year'])).cumsum() / data['Denominator']
    data['O&M Contribution']         = (data['O&M']                 / (1+Discount)**(data['Year'])).cumsum() / data['Denominator']
    data['Fuel Contribution']        = (data['Fuel']                / (1+Discount)**(data['Year'])).cumsum() / data['Denominator']
    data['Electricity Contribution'] = (data['Electricity Revenue'] / (1+Discount)**(data['Year'])).cumsum() / data['Denominator']

    # Generic levelized cost, could be for electricity or heat depending on application
    data['LC'] = data['Numerator']/data['Denominator']
    
    if verbose:
        if application=='electricity':
            print('                                                           LCOE       LCOE       LCOE       LCOE       LCOE')
        else:
            print('                                                           LCOH       LCOH       LCOH       LCOH       LCOH')
        print('Year    Investment  Replacement          O&M         Fuel  CapEx      Repl.      O&M        Fuel       Total')
        print('             [USD]        [USD]        [USD]        [USD]  [USD/MWh]  [USD/MWh]  [USD/MWh]  [USD/MWh]  [USD/MWh]')
        for i in np.arange(0, Duration):
    
            print('{:2.0f}  {:14,.0f} {:12,.0f} {:12,.0f} {:12,.0f}   {:8,.2f}   {:8,.2f}   {:8,.2f}   {:8,.2f}   {:8,.2f}'.format(data['Year'][i], 
                                                       data['Investment'][i],
                                                       data['Replacement'][i],
                                                       data['O&M'][i],
                                                       data['Fuel'][i],
                                                       data['CapEx Contribution'][i],
                                                       data['Replacement Contribution'][i],
                                                       data['O&M Contribution'][i],
                                                       data['Fuel Contribution'][i],                                                  
                                                       data['LC'][i]))
        
        print()
        print('CapEx                    {:10.2f} MUSD'.format(CapEx/1e6))
        print('Power Output             {:10.2f} MW'.format(Power/1e6))
        print('Availability             {:10.2f} %'.format(Availability*100))
        print('Discount Rate            {:10.2f} %'.format(Discount*100))
        
        if application=='Electricity':
        
            print('Overall LCOE               {:8.2f} USD/MWh'.format(data['LC'][Duration-1]))
        
            for key in ['CapEx Contribution', 'Replacement Contribution', 'O&M Contribution', 'Fuel Contribution', 'Electricity Contribution']:
                print('  {:24} {:8.2f} USD/MWh   {:8.2f} %'.format(key, data[key][Duration-1], 100*data[key][Duration-1]/data['LC'][Duration-1]))
                
            # print('Overall LCOE                     {:8.2f} EUR/MWh'.format(data['LC'][Duration-1]*USD_to_EUR))

        else:

            print('Overall LCOH               {:8.2f} USD/MMBTU'.format(data['LC'][Duration-1]/Wh_to_BTU))
        
            for key in ['CapEx Contribution', 'Replacement Contribution', 'O&M Contribution', 'Fuel Contribution', 'Electricity Contribution']:
                print('  {:24} {:8.2f} USD/MMBTU   {:8.2f} %'.format(key, data[key][Duration-1]/Wh_to_BTU, 100*data[key][Duration-1]/data['LC'][Duration-1]))

            # print('Overall LCOH                     {:8.2f} USD/MWh'.format(data['LC'][Duration-1]))
            # print('Overall LCOH                     {:8.2f} EUR/MWh'.format(data['LC'][Duration-1]*USD_to_EUR))

    if save:
        if filename==None:
            if application=='Electricity':
                filename = 'LCOE.csv'
            else:
                filename = 'LCOH.csv'

        data.to_csv(filename)
        
    if application=='Electricity':
        return(data['LC'][Duration-1])
    else:
        return(data['LC'][Duration-1]*1e3/Wh_to_BTU) """
    
def create_radial_build(name, material, thickness, f_vol=1.00):
          
    new_data = pd.DataFrame(data={
        'name':[name], 
        'material':[material], 
        'r_in':[0.0], 
        'r_out':[thickness],
        'f_vol':[f_vol]})
    
    return(new_data)

def add_new_layer(data, name, material, thickness, f_vol=1.00):
    
    # Inner radius is outer radius from last row
    r_in = data['r_out'].values[-1]

    new_data = pd.DataFrame(data={
        'name':[name], 
        'material':[material], 
        'r_in':[r_in], 
        'r_out':[r_in+thickness],
        'f_vol':[f_vol]})
    
    return(pd.concat([data, new_data], ignore_index=True))

def add_fractional_layer(data, name, material, f_vol=1.00):
    
    # Inner radius is inner radius from last row
    r_in = data['r_in'].values[-1]
    r_out = data['r_out'].values[-1]

    new_data = pd.DataFrame(data={
        'name':[name], 
        'material':[material], 
        'r_in':[r_in], 
        'r_out':[r_out],
        'f_vol':[f_vol]})
    
    return(pd.concat([data, new_data], ignore_index=True))

def build_central_cell(inputs):

    radial_build = create_radial_build('Plasma', 'DT', inputs['Central Cell Plasma Radius'])
    radial_build = add_new_layer(radial_build, 'Gap', 'vacuum', inputs['Central Cell Vacuum Gap'])
    radial_build = add_new_layer(radial_build, 'First Wall', inputs['First Wall Material'], inputs['First Wall Thickness'])
    radial_build = add_new_layer(radial_build, 'Vacuum Vessel', inputs['Vacuum Vessel Material'], inputs['Vacuum Vessel Thickness'])
    radial_build = add_new_layer(radial_build, 'Multiplier', inputs['Multiplier Material'], inputs['Multiplier Thicnkess'])
    radial_build = add_new_layer(radial_build, 'Blanket Coolant', inputs['Blanket Coolant Material'], inputs['Blanket Thickness'], inputs['Blanket Coolant Fraction'])
    radial_build = add_fractional_layer(radial_build, 'Blanket Structure', inputs['Blanket Structural Material'], inputs['Blanket Structrual Fraction'])
    radial_build = add_new_layer(radial_build, 'Outer Vessel', inputs['Vacuum Vessel Material'], inputs['Outer Vessel Thickness'])

    return(radial_build)    

def central_cell_cost(inputs, L=1.0):
    return(central_cell(inputs, L=L)['cost'].max())

def central_cell(inputs, L=1.0):
    
    filename = inputs['Cost File']
    
    cost_data = pd.read_csv(filename, index_col=0)
    
    radial_build = build_central_cell(inputs)
    

    
    T = 300 # °C, mean coolant temperture
    
    radial_build['volume'] = np.pi * L * (radial_build['r_out']**2 - radial_build['r_in']**2) * radial_build['f_vol']
    
    # print(radial_build.to_string())

    # print(radial_build)
    
    # Iterate over layer in radial build and calculate volume and cost
    for i in range(len(radial_build)):
   
        material = radial_build['material'][i]
        # print(material)
        
        '''
        PbLi is a special case as the enrichment and temperature affect
        the density and cost. Here the code expects a percent enrichment as
        shown here:
            'Natural PbLi' meaning '7.5% PbLi'
            '93% PbLi' or similar
        '''
        if 'PbLi' in material:
            
            if 'Natural' in material:
                f_6Li = 0.075
            elif '% ' in material:
                f_6Li = float(material.split('% ')[0])/100
            else:
                print('Unable to parse coolant', material)

            radial_build.loc[i, 'density'] = PbLi_density(f_6Li=f_6Li, T=T)
            radial_build.loc[i, 'price'] = PbLi_price(f_6Li, cost_data.loc['Pb']['price'])
            radial_build.loc[i, 'manufacturing_factor'] = 1.0


        else:
   
            radial_build.loc[i, 'density'] = cost_data.loc[material]['density']
            radial_build.loc[i, 'price'] = cost_data.loc[material]['price']
            radial_build.loc[i, 'manufacturing_factor'] = cost_data.loc[material]['manufacturing_factor']

            
        
        radial_build.loc[i, 'mass'] = radial_build['volume'][i] * radial_build['density'][i] 
        radial_build.loc[i, 'cost'] = radial_build['price'][i] * radial_build['mass'][i] * radial_build['manufacturing_factor'][i]
    
    # Add totals to last row
    radial_build = pd.concat([radial_build, pd.DataFrame(data={
        'name':['Total'],
        'cost':[radial_build['cost'].sum()],
        'mass':[radial_build['mass'].sum()]})], ignore_index=True)
    
    radial_build['cost_percent'] = 100 * radial_build['cost'] / radial_build['cost'].max()
    # print()
    # print('Radial build for L =', L)
    # print(radial_build.to_string())
    
    return(radial_build)

    # Return total cost only
    # return(radial_build['cost'].max())



def expander_cell_cost(inputs):
    """
    Each expander cell is made up of:
        A cylindrical vessel
        A DEC convertor
        

    Returns
    -------
    None.
    
    """
    
    # print('Expander Cell')
    
    L = inputs['Expander Cell Length']
    radius = inputs['Expander Cell Radius']
    thickness = inputs['Expander Cell Vessel Thickness']
    vv_material = inputs['Expander Cell Vessel Material']
    
    filename = inputs['Cost File']
    
    cost_data = pd.read_csv(filename, index_col=0)
    
    # Cylindrical shell
    
    radial_build = create_radial_build('Gap', 'vacuum', radius)
    radial_build = add_new_layer(radial_build, 'Vacuum Vessel', vv_material, thickness)
    
    radial_build['volume'] = np.pi * L * (radial_build['r_out']**2 - radial_build['r_in']**2) * radial_build['f_vol']

    for i in range(len(radial_build)):
   
        material = radial_build['material'][i]
        radial_build.loc[i, 'density'] = cost_data.loc[material]['density']
        radial_build.loc[i, 'price'] = cost_data.loc[material]['price']
        radial_build.loc[i, 'manufacturing_factor'] = cost_data.loc[material]['manufacturing_factor']
        radial_build.loc[i, 'mass'] = radial_build['volume'][i] * radial_build['density'][i] 
        radial_build.loc[i, 'cost'] = radial_build['price'][i] * radial_build['mass'][i] * radial_build['manufacturing_factor'][i]
    
    # Add totals to last row
    radial_build = pd.concat([radial_build, pd.DataFrame(data={
        'name':['Total'],
        'cost':[radial_build['cost'].sum()],
        'mass':[radial_build['mass'].sum()]})])
    
    radial_build['cost_percent'] = 100 * radial_build['cost'] / radial_build['cost'].max()
    
    # print(radial_build.to_string())

    # End cap
    V_end_cap = np.pi * thickness * radius**2
    M_end_cap = V_end_cap * cost_data.loc[vv_material]['density']
    C_end_cap = M_end_cap * cost_data.loc[vv_material]['price'] * cost_data.loc[vv_material]['manufacturing_factor']

    # print('End Cap: $', C_end_cap)  
    # print('Cylindrical Part: $', radial_build['cost'].max())
    
    total = 2*C_end_cap + radial_build['cost'].max()
    
    # print('Total: $', total)
    
    return(total)


def HF_magnet_cost(inputs):
    # This is the HF cost per magnet [MUSD], not for all four

    # cost = 500 # high number assuming 25T and 15cm bore, total contained volume ~ magnet volume 
    cost = 29.10 # Assuming ARPA number for WHAM magnet cost, 5x width, using PROCESS J_crit
    cost_factor = (0.70)**(np.log((inputs['Unit Number']-1)*inputs['HF Magnet Number'] + 1)/np.log(2))
    
    return(cost * cost_factor)
    
    
def LF_magnet_cost(inputs):
    # This is the LF cost per magnet [MUSD]

    # cost = 140 # assuming 15cm bore radius and 17T required    
    cost = 6.25262 # ARPA WHAM cost, 100cm bore, PROCESS jcrit, 10T required

    cost_factor = (0.70)**(np.log((inputs['Unit Number']-1)*inputs['LF Magnet Number'] + 1)/np.log(2))
    
    return(cost * cost_factor)
    
def CF_magnet_cost(inputs):
    # This is the CF cost per magnet [MUSD]

    # Put in your own value here!  This is merely a placeholder.
    
    cost = 2.1*1.31 # Assuming 700k/Tesla in 2016 dollars with 3T LTS
    cost_factor = (0.70)**(np.log((inputs['Unit Number']-1)*inputs['CF Magnet Number'] + 1)/np.log(2))
    
    return(cost * cost_factor)

def HF_magnet_shield_cost(inputs, verbose=False):
    """
    

    The HF coils have annular shield with a U-shaped cross section:
    
             +----+--------+----+
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             +----+--------+----+
              \   |        |   /
               \  |        |  /
                \ |        | /
                 \|        |/ 
                  +--------+
                
            
             - - - - - - - - - - - Center Line    
             
             
                  +--------+
                 /|        |\
                / |        | \
               /  |        |  \
              /   |        |   \
             +----+--------+----+
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             |    |xxxxxxxx|    |
             +----+--------+----+    
    

    """
    
    # Shielding thickness should be on the same order as the bore radius (~30 cm - 1m)
    # It's a reasonable assumption to say that all axial widths/layers will be the same


    filename = inputs['Cost File']
    cost_data = pd.read_csv(filename, index_col=0)    

    # Eventually these will be arguments
    material = 'W'
    a_M = 0.15 # From Frank
    a_CC = 0.54 # From Frank
    a_0 = 0.7 

    # Radially Inner Cylinder
    # length = 4.5 # End plug length from Frank
    length = 0.5 # Is this the required shielding thickness?
    a_M = 0.15 
    r_gap = 0.1 # General advice via Hitarth: lower inner radius -> thicker shielding
    r_vv = 0.01 # Reduced from 0.1 to 0.01
    
    # r_magnet = 1.0 # original
    r_magnet = 1.5 # From Frank and confirmed (1.45) in magnet cost guesses
    r_cryostat = 1.0
    
    f_vol = 0.90
    
    
    r_in = a_M + r_gap + r_vv
    r_out = r_magnet - r_cryostat
    
    V_radially_inner_cylinder = V_cylindrical_shell(r_in, r_out, length) * f_vol

    # Central Cell Cylinder
    # length_cc_cylinder = 50.0
    length_cc_cylinder = 0.5
    r_in_cc = a_CC + r_gap + r_vv
    # r_out_cc = 1.0
    r_out_cc = r_in_cc+0.5

    V_cc_cylinder = V_cylindrical_shell(r_in_cc, r_out_cc, length_cc_cylinder) * f_vol
    
    # Central Cell Triangular Washer
    V_cc_triangle = V_inverse_triangular_washer(length_cc_cylinder, r_in, r_in_cc) * f_vol
    
    # End Plug Cylinder
    length_ep_cylinder = 0.5 # From Frank
    r_in_ep = a_0 + r_gap + r_vv
    r_out_ep = r_in_ep + 0.5

    V_ep_cylinder = V_cylindrical_shell(r_in_ep, r_out_ep, length_ep_cylinder) * f_vol
    
    # End Cell Triangular Washer
    V_ep_triangle = V_inverse_triangular_washer(length_ep_cylinder, r_in, r_in_ep) * f_vol

    # For central cell facing magnet, add up all five regions
    V_total_cc_facing = V_radially_inner_cylinder + V_cc_cylinder + V_cc_triangle + V_ep_cylinder + V_ep_triangle

    # For expander cell facing magnet, only add up three regions
    # No neutrons come from the expander cell
    V_total_ec_facing = V_radially_inner_cylinder +  V_ep_cylinder + V_ep_triangle

    # Summary information
    V_total = V_total_cc_facing + V_total_ec_facing
    mass = cost_data.loc[material]['density'] * V_total
    cost = cost_data.loc[material]['price'] * cost_data.loc[material]['manufacturing_factor'] * mass


    if verbose:
        print('Central Cell Facing Magnet Volume Calculation')
        print('  Radially Inner Cylinder {:12.2f} m^3'.format(V_radially_inner_cylinder))
        print('  Central Cell Cylinder   {:12.2f} m^3'.format(V_cc_cylinder))
        print('  Central Cell Triangle   {:12.2f} m^3'.format(V_cc_triangle))
        print('  End Plug Cylinder       {:12.2f} m^3'.format(V_ep_cylinder))
        print('  End Plug Triangle       {:12.2f} m^3'.format(V_ep_triangle))
        print('  Total                   {:12.2f} m^3'.format(V_total_cc_facing))
        print()
        
        
        print('Expander Cell Facing Magnet Volume Calculation')
        print('  Radially Inner Cylinder {:12.2f} m^3'.format(V_radially_inner_cylinder))
        print('  End Plug Cylinder       {:12.2f} m^3'.format(V_ep_cylinder))
        print('  End Plug Triangle       {:12.2f} m^3'.format(V_ep_triangle))
        print('  Total                   {:12.2f} m^3'.format(V_total_ec_facing))
        print()
        
        print('Shield Totals')
        print('  Volume                  {:12.2f} m^3'.format(V_total))
        print('  Density                 {:12.2f} kg/m^3'.format(cost_data.loc[material]['density']))
        print('  Mass                    {:12.2f} kg'.format(mass))
        print('  Price                   {:12.2f} USD/kg'.format(cost_data.loc[material]['price']))
        print('  Manufacturing Factor    {:12.2f}'.format(cost_data.loc[material]['manufacturing_factor']))
        print('  Cost                    {:12.2f} MUSD'.format(cost/1e6))
        print()

    return(cost)
