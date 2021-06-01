#this is the PLC 1 logic, it's about the very same thing as that in the real plc.
from logicblock.logicblock import SETD
from logicblock.logicblock import TONR
from controlblock.controlblock import *

class plc1:
	'plc1 logic'
	
	def __init__(self,HMI):
		self.LIT101_FB = AIN_FBD(HMI.LIT101)                                 # Tank level indicating transmitter function block
		self.MV101_FB = MV_FBD(HMI.MV101)                                    # Motorized valve funtion block
		self.FIT101_FB = FIT_FBD(HMI.FIT101)                                 # Water flow indicating transmitter
		self.P101_FB = PMP_FBD(HMI.P101)                                     # P101/2 function block
		self.P102_FB = PMP_FBD(HMI.P102)
		self.P_RAW_WATER_DUTY_FB = Duty2_FBD()                               # Choose one pump to start

		self.TON_FIT102_P1_TM = TONR(10, 'FIT102_P1')                        # Max cost time (10s) to be normal after enable FIT102 for P101/2
		self.TON_FIT102_P2_TM = TONR(10, 'FIT102_P2')

		self.Mid_MV101_AutoInp = HMI.MV101.Status-1                          # Whether open MV101
		self.Mid_P_RAW_WATER_DUTY_AutoInp = HMI.P101.Status-1                # Whether start raw water process pump
		print("	PLC1 started\n")

	def Pre_Main_Raw_Water(self,IO,HMI):
		if HMI.PLANT.Reset_On:
			HMI.MV101.Reset = 1
			HMI.P101.Reset 	= 1
			HMI.P102.Reset 	= 1
		if HMI.PLANT.Auto_On:
			HMI.MV101.Auto 	= 1
			HMI.P101.Auto 	= 1
			HMI.P102.Auto 	= 1
		if HMI.PLANT.Auto_Off:
			HMI.MV101.Auto = 0
			HMI.P101.Auto  = 0
			HMI.P102.Auto  = 0

		HMI.P1.Permissive_On = HMI.MV101.Avl and (HMI.P101.Avl or HMI.P102.Avl)
		HMI.PLANT.Ready = HMI.P1.Permissive_On and HMI.P2.Permissive_On and HMI.P3.Permissive_On and HMI.P4.Permissive_On

		HMI.P101.Permissive[0] = HMI.LIT101.Hty and not HMI.LIT101.ALL
		HMI.P101.Permissive[1] = HMI.MV201.Status == 2

		HMI.P101.MSG_Permissive[1] = HMI.P101.Permissive[0]
		HMI.P101.MSG_Permissive[2] = HMI.P101.Permissive[1]

		HMI.P102.Permissive[0] = HMI.LIT101.Hty and not HMI.LIT101.ALL
		HMI.P102.Permissive[1] = (HMI.MV201.Status == 2)

		HMI.P102.MSG_Permissive[1] = HMI.P102.Permissive[0]
		HMI.P102.MSG_Permissive[2] = HMI.P102.Permissive[1]

		HMI.P101.SD[0] = HMI.LIT101.Hty and HMI.LIT101.ALL
		HMI.P101.SD[1] = HMI.P101.Status == 2 and HMI.MV201.Status != 2
		HMI.P101.SD[2] = self.TON_FIT102_P1_TM.DN

		HMI.P101.MSG_Shutdown[1] = HMI.P101.Shutdown[0]
		HMI.P101.MSG_Shutdown[2] = HMI.P101.Shutdown[1]
		HMI.P101.MSG_Shutdown[3] = HMI.P101.Shutdown[2]

		HMI.P102.SD[0] = HMI.LIT101.Hty and HMI.LIT101.ALL
		HMI.P102.SD[1] = HMI.P102.Status == 2 and HMI.MV201.Status != 2
		HMI.P102.SD[2] = self.TON_FIT102_P2_TM.DN

		HMI.P102.MSG_Shutdown[1] = HMI.P102.Shutdown[0]
		HMI.P102.MSG_Shutdown[2] = HMI.P102.Shutdown[1]
		HMI.P102.MSG_Shutdown[3] = HMI.P102.Shutdown[2]

	#def Main_Seq(self,Min_P):
		if HMI.PLANT.Stop:
			HMI.P1.Shutdown = 1

		if HMI.P1.State == 1:
			self.Mid_MV101_AutoInp = 0
			self.Mid_P_RAW_WATER_DUTY_AutoInp = 0
			HMI.P1.Ready = 0
			if HMI.PLANT.Ready and HMI.PLANT.Start and HMI.P1.Permissive_On:
				HMI.P1.State = 2

		elif HMI.P1.State == 2:
			self.Mid_MV101_AutoInp = SETD(HMI.LIT101.AL, HMI.LIT101.AH, self.Mid_MV101_AutoInp)
			self.Mid_P_RAW_WATER_DUTY_AutoInp = SETD(HMI.MV201.Status == 2 and HMI.LIT301.AL,
													 HMI.MV201.Status != 2 or HMI.LIT301.AH,
													 self.Mid_P_RAW_WATER_DUTY_AutoInp)
			if HMI.P1.Shutdown:
				HMI.P1.State = 3
				HMI.P1.Shutdown = 0

		elif HMI.P1.State == 3:
			self.Mid_MV101_AutoInp = SETD(HMI.LIT101.AL, HMI.LIT101.AH, self.Mid_MV101_AutoInp)
			self.Mid_P_RAW_WATER_DUTY_AutoInp = SETD(HMI.MV201.Status == 2 and HMI.LIT301.AL,
													 HMI.MV201.Status != 2 or HMI.LIT301.AH,
													 self.Mid_P_RAW_WATER_DUTY_AutoInp)

			if HMI.LIT101.AH and HMI.LIT301.AH:
				self.Mid_MV101_AutoInp = 0
				self.Mid_P_RAW_WATER_DUTY_AutoInp = 0
				HMI.P1.State = 2

			if HMI.P1.Shutdown:
				HMI.P1.State = 1
				HMI.P1.Shutdown = 0

#	def Raw_Water(self,Min_P,Sec_P):
		self.MV101_FB.MV_FBD(self.Mid_MV101_AutoInp, IO.MV101, HMI.MV101)
		self.P_RAW_WATER_DUTY_FB.Duty2_FBD(self.Mid_P_RAW_WATER_DUTY_AutoInp, HMI.P101, HMI.P102, HMI.P_RAW_WATER_DUTY)
		self.P101_FB.PMP_FBD(self.P_RAW_WATER_DUTY_FB.Start_Pmp1, IO.P101, HMI.P101)
		self.P102_FB.PMP_FBD(self.P_RAW_WATER_DUTY_FB.Start_Pmp2, IO.P102, HMI.P102)