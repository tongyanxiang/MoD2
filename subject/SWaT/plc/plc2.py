#this is the PLC 2 logic, it's about the very same thing as that in the real plc.
from logicblock.logicblock import SETD
from logicblock.logicblock import TONR
from controlblock.controlblock import *

class plc2:
	'plc2 logic'

	def __init__(self, HMI):
		self.MV201_FB = MV_FBD(HMI.MV201)
		self.LS201_FB = SWITCH_FBD(HMI.LS201)                              # T-201: NaCl
		self.LS202_FB = SWITCH_FBD(HMI.LS202)                              # T-202: HCl
		self.LS203_FB = SWITCH_FBD(HMI.LSL203)                             # T-203: NaOCl
		self.LSLL203_FB = SWITCH_FBD(HMI.LSLL203)
		self.P201_FB = PMP_FBD(HMI.P201)                                   # NaCl dosing pump
		self.P202_FB = PMP_FBD(HMI.P202)
		self.P203_FB = PMP_FBD(HMI.P203)                                   # HCl dosing pump
		self.P204_FB = PMP_FBD(HMI.P204)
		self.P205_FB = PMP_FBD(HMI.P205)                                   # NaOCl dosing pump
		self.P206_FB = PMP_FBD(HMI.P206)
		self.P207_FB = PMP_FBD(HMI.P207)                                   # NaOCl dosing pump to UF cleaning
		self.P208_FB = PMP_FBD(HMI.P208)
		self.P_NACL_DUTY_FB = Duty2_FBD()
		self.P_HCL_DUTY_FB = Duty2_FBD()
		self.P_NAOCL_FAC_DUTY_FB = Duty2_FBD()
		self.FIT201_FB = FIT_FBD(HMI.FIT201)
		self.AIT201_FB = AIN_FBD(HMI.AIT201)                               # cond: Conductivity (µS/cm)
		self.AIT202_FB = AIN_FBD(HMI.AIT202)                               # pH
		self.AIT203_FB = AIN_FBD(HMI.AIT203)                               # ORP: Oxidation Reduction Potential (mV)

		self.TON_FIT102_P1_TM = TONR("FIT102_P1")
		self.TON_FIT102_P2_TM = TONR("FIT102_P2")
		self.TON_FIT102_P3_TM = TONR("FIT102_P3")
		self.TON_FIT102_P4_TM = TONR("FIT102_P4")
		self.TON_FIT102_P5_TM = TONR("FIT102_P5")
		self.TON_FIT102_P6_TM = TONR("FIT102_P6")

		self.Mid_MV201_AutoInp = HMI.MV201.Status-1
		self.Mid_P_NACL_DUTY_AutoInp = HMI.P201.Status-1
		self.Mid_P_HCL_DUTY_AutoInp = HMI.P203.Status-1
		self.Mid_P_NAOCL_FAC_DUTY_AutoInp = HMI.P205.Status-1
		self.Mid_FIT201_Tot_Enb = 0

		print("	PLC2 Started\n")

	def Pre_Main_UF_Feed_Dosing(self, IO, HMI):
		if HMI.PLANT.Reset_On:
			HMI.MV201.Reset	= 1
			HMI.P201.Reset = 1
			HMI.P202.Reset = 1
			HMI.P203.Reset = 1
			HMI.P204.Reset = 1
			HMI.P205.Reset = 1
			HMI.P206.Reset = 1
			HMI.P207.Reset = 1
			HMI.P208.Reset = 1

		if HMI.PLANT.Auto_On:
			HMI.MV201.Auto = 1
			HMI.P201.Auto = 1
			HMI.P202.Auto = 1
			HMI.P203.Auto = 1
			HMI.P204.Auto = 1
			HMI.P205.Auto = 1
			HMI.P206.Auto = 1
			HMI.P207.Auto = 1
			HMI.P208.Auto = 1
		
		if HMI.PLANT.Auto_Off:
			HMI.MV201.Auto = 0
			HMI.P201.Auto = 0
			HMI.P202.Auto = 0
			HMI.P203.Auto = 0
			HMI.P204.Auto = 0
			HMI.P205.Auto = 0
			HMI.P206.Auto = 0
			HMI.P207.Auto = 0
			HMI.P208.Auto = 0
		
		HMI.P2.Permissive_On = HMI.MV201.Avl and (HMI.P201.Avl or HMI.P202.Avl) and (HMI.P203.Avl or HMI.P204.Avl) and (HMI.P205.Avl or HMI.P206.Avl)

		self.Mid_FIT201_Tot_Enb = (HMI.MV201.Status == 2) # MV201 opens => FIT201 can be enable

		# MV201 opens and related pumps start but water flow is super low, FIT201 fault timer add 1
		self.TON_FIT102_P1_TM.TONR(HMI.FIT201.ALL and HMI.MV201.Status == 2 and HMI.P201.Status == 2)
		self.TON_FIT102_P2_TM.TONR(HMI.FIT201.ALL and HMI.MV201.Status == 2 and HMI.P202.Status == 2)
		self.TON_FIT102_P3_TM.TONR(HMI.FIT201.ALL and HMI.MV201.Status == 2 and HMI.P203.Status == 2)
		self.TON_FIT102_P4_TM.TONR(HMI.FIT201.ALL and HMI.MV201.Status == 2 and HMI.P204.Status == 2)
		self.TON_FIT102_P5_TM.TONR(HMI.FIT201.ALL and HMI.MV201.Status == 2 and HMI.P205.Status == 2)
		self.TON_FIT102_P6_TM.TONR(HMI.FIT201.ALL and HMI.MV201.Status == 2 and HMI.P206.Status == 2)

		HMI.P201.Permissive[0] = not HMI.LS201.Alarm
		HMI.P201.Permissive[1] = HMI.MV201.Status == 2
		HMI.P201.Permissive[2] = HMI.FIT201.AH                    # Water flow is high

		HMI.P201.MSG_Permissive[1] = HMI.P201.Permissive[0]
		HMI.P201.MSG_Permissive[2] = HMI.P201.Permissive[1]
		HMI.P201.MSG_Permissive[3] = HMI.P201.Permissive[2]

		HMI.P202.Permissive[0] = not HMI.LS201.Alarm
		HMI.P202.Permissive[1] = HMI.MV201.Status == 2
		HMI.P202.Permissive[2] = HMI.FIT201.AH

		HMI.P202.MSG_Permissive[1] = HMI.P202.Permissive[0]
		HMI.P202.MSG_Permissive[2] = HMI.P202.Permissive[1]
		HMI.P202.MSG_Permissive[3] = HMI.P202.Permissive[2]

		HMI.P203.Permissive[0] = not HMI.LS202.Alarm
		HMI.P203.Permissive[1] = HMI.MV201.Status == 2
		HMI.P203.Permissive[2] = HMI.FIT201.AH

		HMI.P203.MSG_Permissive[1] = HMI.P203.Permissive[0]
		HMI.P203.MSG_Permissive[2] = HMI.P203.Permissive[1]
		HMI.P203.MSG_Permissive[3] = HMI.P203.Permissive[2]

		HMI.P204.Permissive[0] = not HMI.LS202.Alarm
		HMI.P204.Permissive[1] = HMI.MV201.Status == 2
		HMI.P204.Permissive[2] = HMI.FIT201.AH

		HMI.P204.MSG_Permissive[1] = HMI.P204.Permissive[0]
		HMI.P204.MSG_Permissive[2] = HMI.P204.Permissive[1]
		HMI.P204.MSG_Permissive[3] = HMI.P204.Permissive[2]

		HMI.P205.Permissive[0] = not HMI.LSL203.Alarm
		HMI.P205.Permissive[1] = HMI.MV201.Status == 2
		HMI.P205.Permissive[2] = HMI.FIT201.AH

		HMI.P205.MSG_Permissive[1] = HMI.P205.Permissive[0]
		HMI.P205.MSG_Permissive[2] = HMI.P205.Permissive[1]
		HMI.P205.MSG_Permissive[3] = HMI.P205.Permissive[2]

		HMI.P206.Permissive[0] = not HMI.LSL203.Alarm
		HMI.P206.Permissive[1] = HMI.MV201.Status == 2
		HMI.P206.Permissive[2] = HMI.FIT201.AH

		HMI.P206.MSG_Permissive[1] = HMI.P206.Permissive[0]
		HMI.P206.MSG_Permissive[2] = HMI.P206.Permissive[1]
		HMI.P206.MSG_Permissive[3] = HMI.P206.Permissive[2]

		HMI.P207.Permissive[0] = not HMI.LSL203.Alarm
		HMI.P207.Permissive[1] = HMI.MV301.Status == 2

		HMI.P207.MSG_Permissive[1] = HMI.P207.Permissive[0]
		HMI.P207.MSG_Permissive[2] = HMI.P207.Permissive[1]
		HMI.P207.MSG_Permissive[3] = HMI.P207.Permissive[2]

		HMI.P208.Permissive[0] = not HMI.LSL203.Alarm
		HMI.P208.Permissive[1] = HMI.MV301.Status == 2

		HMI.P208.MSG_Permissive[1] = HMI.P208.Permissive[0]
		HMI.P208.MSG_Permissive[2] = HMI.P208.Permissive[1]
		HMI.P208.MSG_Permissive[3] = HMI.P208.Permissive[2]

		HMI.P201.SD[0] = HMI.LS201.Alarm
		HMI.P201.SD[1] = HMI.P201.Status == 2 and HMI.MV201.Status != 2
		HMI.P201.SD[2] = self.TON_FIT102_P1_TM.DN

		HMI.P201.MSG_Shutdown[1] = HMI.P201.Shutdown[0]
		HMI.P201.MSG_Shutdown[2] = HMI.P201.Shutdown[1]
		HMI.P201.MSG_Shutdown[3] = HMI.P201.Shutdown[2]

		HMI.P202.SD[0] = HMI.LS201.Alarm
		HMI.P202.SD[1] = HMI.P201.Status == 2 and HMI.MV201.Status != 2
		HMI.P202.SD[2] = self.TON_FIT102_P2_TM.DN

		HMI.P202.MSG_Shutdown[1] = HMI.P202.Shutdown[0]
		HMI.P202.MSG_Shutdown[2] = HMI.P202.Shutdown[1]
		HMI.P202.MSG_Shutdown[3] = HMI.P202.Shutdown[2]

		HMI.P203.SD[0] = HMI.LS202.Alarm
		HMI.P203.SD[1] = HMI.P201.Status == 2 and HMI.MV201.Status != 2
		HMI.P203.SD[2] = self.TON_FIT102_P3_TM.DN

		HMI.P203.MSG_Shutdown[1] = HMI.P203.Shutdown[0]
		HMI.P203.MSG_Shutdown[2] = HMI.P203.Shutdown[1]
		HMI.P203.MSG_Shutdown[3] = HMI.P203.Shutdown[2]

		HMI.P204.SD[0] = HMI.LS202.Alarm
		HMI.P204.SD[1] = HMI.P201.Status == 2 and HMI.MV201.Status != 2
		HMI.P204.SD[2] = self.TON_FIT102_P4_TM.DN

		HMI.P204.MSG_Shutdown[1] = HMI.P204.Shutdown[0]
		HMI.P204.MSG_Shutdown[2] = HMI.P204.Shutdown[1]
		HMI.P204.MSG_Shutdown[3] = HMI.P204.Shutdown[2]

		HMI.P205.SD[0] = HMI.LSL203.Alarm
		HMI.P205.SD[1] = HMI.P201.Status == 2 and HMI.MV201.Status != 2
		HMI.P205.SD[2] = self.TON_FIT102_P5_TM.DN

		HMI.P205.MSG_Shutdown[1] = HMI.P205.Shutdown[0]
		HMI.P205.MSG_Shutdown[2] = HMI.P205.Shutdown[1]
		HMI.P205.MSG_Shutdown[3] = HMI.P205.Shutdown[2]

		HMI.P206.SD[0] = HMI.LSL203.Alarm
		HMI.P206.SD[1] = HMI.P201.Status == 2 and HMI.MV201.Status != 2
		HMI.P206.SD[2] = self.TON_FIT102_P6_TM.DN

		HMI.P206.MSG_Shutdown[1] = HMI.P206.Shutdown[0]
		HMI.P206.MSG_Shutdown[2] = HMI.P206.Shutdown[1]
		HMI.P206.MSG_Shutdown[3] = HMI.P206.Shutdown[2]

		HMI.P207.SD[0] = HMI.LSL203.Alarm
		HMI.P207.SD[1] = HMI.P207.Status == 2 and HMI.MV301.Status != 2

		HMI.P207.MSG_Shutdown[1] = HMI.P207.Shutdown[0]
		HMI.P207.MSG_Shutdown[2] = HMI.P207.Shutdown[1]

		HMI.P208.SD[0] = HMI.LSL203.Alarm
		HMI.P208.SD[1] = HMI.P207.Status == 2 and HMI.MV301.Status != 2

		HMI.P208.MSG_Shutdown[1] = HMI.P208.Shutdown[0]
		HMI.P208.MSG_Shutdown[2] = HMI.P208.Shutdown[1]

	# def Main(self)
		if HMI.PLANT.Stop or HMI.PLANT.Critical_SD_On: # HMI.PLANT.Critical_SD_On variable could be rethought, currently it's defined in HMI
			HMI.P2.Shutdown = 1

		if HMI.P2.State == 1:
			self.Mid_MV201_AutoInp = 0
			self.Mid_P_NACL_DUTY_AutoInp = 0
			self.Mid_P_HCL_DUTY_AutoInp = 0
			self.Mid_P_NAOCL_FAC_DUTY_AutoInp = 0

			if HMI.P2.Permissive_On and HMI.PLANT.Start:
				HMI.P2.State = 2

		elif HMI.P2.State == 2:
			#(*MV-201 , Raw Water Outlet Valve Control*)	
			self.Mid_MV201_AutoInp = SETD(HMI.LIT301.AL, HMI.LIT301.AH, self.Mid_MV201_AutoInp)
			
			#(*P-201/2 , Cond NACL Dosing Pump Control*)
			# Start P101/2 when MV201 opens and P2's conductivity is low and P5's conductivity is not high
			# Stop P101/2 when MV201 doesn't open or P2's conductivity is high or P5's conductivity is high or tank level of T-201 is low or P2's water flow rate is super low
			self.Mid_P_NACL_DUTY_AutoInp  = SETD(HMI.MV201.Status == 2 and (HMI.AIT201.AL) and (not HMI.AIT503.AH),
												 HMI.MV201.Status != 2 or (HMI.AIT201.AH) or (HMI.AIT503.AH) or HMI.LS201.Alarm or HMI.FIT201.ALL,
												 self.Mid_P_NACL_DUTY_AutoInp)

			#(*P-203/4 , PH HCL Dosing Pump Control*)
			# Start P103/4 when MV201 opens and P2's pH is high
			# Stop P103/4 when MV201 doesn't open or P2's pH is low or tank level of T-202 is low or P2's water flow rate is super low
			self.Mid_P_HCL_DUTY_AutoInp = SETD( HMI.MV201.Status == 2 and (HMI.AIT202.AH),
												HMI.MV201.Status != 2 or (HMI.AIT202.AL) or HMI.LS202.Alarm or HMI.FIT201.ALL,
												self.Mid_P_HCL_DUTY_AutoInp)

			#(*P-205/6 ,ORP NAOCL FAC Dosing Pump Control*)
			# Start P105/6 when MV201 opens and P2's ORP is low and P4's ORP is not high
			# Stop P105/6 when MV201 doesn't open or P2's ORP is high or P4's conductivity is high or tank level of T-203 is super low
			self.Mid_P_NAOCL_FAC_DUTY_AutoInp = SETD( HMI.MV201.Status == 2 and (HMI.AIT203.AL) and (not HMI.AIT402.AH),
													  HMI.MV201.Status != 2 or (HMI.AIT203.AH) or (HMI.AIT402.AH) or HMI.LSL203.Alarm,
													  self.Mid_P_NAOCL_FAC_DUTY_AutoInp)

			HMI.P2.Ready = 1
			if HMI.P2.Shutdown:
				if HMI.LIT301.AH:
					HMI.P2.State = 1
					HMI.P2.Shutdown	= 0
		else:	
			HMI.P2.State = 1

		self.MV201_FB.MV_FBD(self.Mid_MV201_AutoInp, IO.MV201,HMI.MV201)
		self.LS201_FB.SWITCH_FBD(IO.LS201, HMI.LS201)
		self.LS201_FB.SWITCH_FBD(IO.LS202, HMI.LS202)
		self.LS203_FB.SWITCH_FBD(IO.LSL203, HMI.LSL203)
		self.LSLL203_FB.SWITCH_FBD(IO.LSL203, HMI.LSLL203)
		self.P_NACL_DUTY_FB.Duty2_FBD(self.Mid_P_NACL_DUTY_AutoInp, HMI.P201,HMI.P202,HMI.P_NACL_DUTY)
		self.P_HCL_DUTY_FB.Duty2_FBD(self.Mid_P_HCL_DUTY_AutoInp, HMI.P203,HMI.P204,HMI.P_HCL_DUTY)
		self.P_NAOCL_FAC_DUTY_FB.Duty2_FBD(self.Mid_P_NAOCL_FAC_DUTY_AutoInp, HMI.P205,HMI.P206,HMI.P_NAOCL_FAC_DUTY)
		self.P201_FB.PMP_FBD(self.P_NACL_DUTY_FB.Start_Pmp1, IO.P201, HMI.P201)
		self.P202_FB.PMP_FBD(self.P_NACL_DUTY_FB.Start_Pmp2, IO.P202, HMI.P202)
		self.P203_FB.PMP_FBD(self.P_HCL_DUTY_FB.Start_Pmp1, IO.P203, HMI.P203)
		self.P204_FB.PMP_FBD(self.P_HCL_DUTY_FB.Start_Pmp2, IO.P204, HMI.P204)
		self.P205_FB.PMP_FBD(self.P_NAOCL_FAC_DUTY_FB.Start_Pmp1,IO.P205, HMI.P205)
		self.P206_FB.PMP_FBD(self.P_NAOCL_FAC_DUTY_FB.Start_Pmp2,IO.P206, HMI.P206)