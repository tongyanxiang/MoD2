from logicblock.logicblock import ALM

class HMI_plant:
	def __init__(self):
		self.Reset_On = 1              # Fault signal parameters (e.g., FTO) of MV and pumps are set to 0
		self.Auto_On  = 1
		self.Auto_Off = 0
		self.Ready    = 1
		self.Start    = 1
		self.Stop     = 0              # Stop=1: HMI_Phase.Shutdown=1
		self.Critical_SD_On = 0        # Need to rethought
		self.TMP_High = 0              # TMP_High = DPIT301.AH

class HMI_phase:
	def __init__(self):
		self.Permissive_On = 1         # All MVs and Pumps are in normal state
		self.Shutdown = 1              # Stop=1: HMI_Phase.Shutdown=1
		self.State    = 1              # State=1: Ready=0
		self.Ready    = 0
		self.TMP_High = 0              # TMP_High for P3
		
class HMI_Ultralfiltration_Cycle:
	def __init__(self):
		self.UF_REFILL_SEC = 0         # UF flushing procedure (30s)
		self.UF_FILTRATION_MIN = 0     # UF ultra filtration procedure (3min)
		self.BACKWASH_SEC = 0          # UF back wash procedure (30s)
		self.CIP_CLEANING_SEC = 0
		self.DRAIN_SEC = 0             # UF feed tank draining procedure (30s)

		self.UF_REFILL_SEC_SP = 30
		self.UF_FILTRATION_MIN_SP = 3  # original value is 30 min, lets put it shorter so to cater test time budget
		self.BACKWASH_SEC_SP = 30
		self.DRAIN_SEC_SP = 30
		self.CIP_CLEANING_SEC_SP = 0
		self.BW_CNT = 0

class HMI_ReverseOsmosis_Cycle:
	def __init__(self):
		self.RO_TMP = 0
		self.HPP_Q_MAX_M3H = 0
		self.HMI_HPP_Q_SET_M3H = 0
		self.MIN_RO_VSD_SPEED = 0
		self.RAMPING_RATE_ER_SEC = 0
		self.VSD_MIN_SPEED = 0
		self.VSD_HIGH_SPEED = 0
		self.MV501_TIMEOUT_TM = 0
		self.MV502_TIMEOUT_TM = 0
		self.MV503_TIMEOUT_TM = 0
		self.MV504_TIMEOUT_TM = 0
		self.RO_HPP_SD_On = 0
		self.FLUSHING_MIN = 0
		self.FLUSHING_MIN_SP = 2       # temporarily set to this value
		self.RO_HIGH_PUMP_Shutdown = 0
		self.SD_FLUSHING_DONE_On = 0
		self.RO_SD_FLUSHING = 0
		self.RO_SD_FLUSHING_MIN = 0

class HMI_mv:
	def __init__(self):
		self.Auto = 1                  # Set Cmd based on (plant) MV I/Os signals
		self.Reset = 1                 # Reset fault signal parameters: FTO=0 and FTC=0
		self.FTO = 0                   # Fail to open alarm
		self.FTC = 0                   # Fail to close alarm
		self.Status = 0                # MV status based on signals from plant through I/Os
		self.Avl = 1                   # Whether MV is in normal state
		self.Cmd = 1                   # MV user command (not auto)
		self.Open = 1                  # Initial MV open command
		self.Close = 0                 # Initial MV close command

class HMI_pump:
	def __init__(self):
		self.Auto = 1
		self.Permissive = [1] * 32     # Whether the conditions to open the pump are satisfied (one column for one condition)
		self.MSG_Permissive = [0] * 6  # Actually values [1-5] is needed, but for expressiveness, we difine from [0-5]
		self.SD = [0] * 32             # Whether the conditions to shutdown the pump are satisfied (one column for one condition)
		self.MSG_Shutdown = [0] * 6
		self.Reset = 0                 # Reset faulty signal parameters: FT_Start=0, FT_Stop=0 and SD=0
		self.Reset_RunHr = 0
		self.FTR = 0                   # Pump faulty start parameter
		self.FTS = 0                   # Pump faulty stop parameter
		self.RunHr = 0
		self.Total_RunHr = 0
		self.Pump_Running = 0
		self.Status = 1
		self.Avl = 1                   # whether pump is in normal state
		self.Fault = 0
		self.Cmd = 1                   # Pump user command (not auto)
		self.Shutdown = [0] * 32       # Initial shutdown conditions

class HMI_uv:
	def __init__(self):
		self.Auto = 1
		self.Permissive = [1] * 32     # Whether the conditions to open the pump are satisfied (one column for one condition)
		self.MSG_Permissive = [0] * 6  # Actually values [1-5] is needed, but for expressiveness, we difine from [0-5]
		self.SD = [0] * 32             # Whether the conditions to shutdown the pump are satisfied (one column for one condition)
		self.MSG_Shutdown = [0] * 6
		self.Reset = 0                 # Reset faulty signal parameters: FT_Start=0, FT_Stop=0 and SD=0
		self.Reset_RunHr = 0
		self.FTR = 0                   # Pump faulty start parameter
		self.FTS = 0                   # Pump faulty stop parameter
		self.RunHr = 0
		self.Total_RunHr = 0
		self.Status = 1
		self.Avl = 1                   # whether pump is in normal state
		self.Fault = 0
		self.Cmd = 1                   # Pump user command (not auto)
		self.Shutdown = [0] * 32       # Initial shutdown conditions

class HMI_LIT:
	def __init__(self, SAHH, SAH, SAL, SALL):
		self.SAHH = SAHH               # Sensor alarm value
		self.SAH = SAH
		self.SAL = SAL
		self.SALL = SALL
		self.Hty  = 1                  # whether tank level sensor return value is in the defined low and high bounds
		self.AHH = 0                   # Sensor alarm
		self.AH  = 0
		self.AL  = 0
		self.ALL = 0
		self.Pv = 0

	def set_alarm(self):
		if type(self.Pv) != type('a'):
			self.AHH, self.AH, self.AL, self.ALL = ALM(self.Pv, self.SAHH, self.SAH, self.SAL, self.SALL)
		else:
			print(self.Pv)

class HMI_FIT:
	def __init__(self, SAHH, SAH, SAL, SALL):
		self.SAHH = SAHH
		self.SAH = SAH
		self.SAL = SAL
		self.SALL = SALL
		self.Rst_Totaliser = 0
		self.Hty  = 0
		self.AHH  = 0
		self.AH   = 0
		self.AL   = 0
		self.ALL  = 0
		self.Totaliser = 0
		self.Pv = 0

	def set_alarm(self):
		if type(self.Pv) != type('a'):
			self.AHH, self.AH, self.AL, self.ALL = ALM(self.Pv, self.SAHH, self.SAH, self.SAL, self.SALL)

class HMI_duty2:
	def __init__(self):
		self.Selection = 1
		self.Both_Pmp_Not_Avl = 0
		self.Selected_Pmp_Not_Avl = 0
		
class HMI_ait:
	def __init__(self,SAHH,SAH,SAL,SALL):
		self.SAHH = SAHH
		self.SAH  = SAH
		self.SAL  = SAL
		self.SALL = SALL
		self.Hty  = 0
		self.AHH  = 0
		self.AH   = 0
		self.AL   = 0
		self.ALL  = 0
		self.Pv = 0

	def set_alarm(self):
		if type(self.Pv) != type('a'):
			self.AHH, self.AH, self.AL, self.ALL = ALM(self.Pv, self.SAHH, self.SAH, self.SAL, self.SALL)

class HMI_PSH:
	def __init__(self):
		self.Delay = [0] * 32
		self.Alarm = 0

class HMI_DPSH:
	def __init__(self):
		self.Delay = [0] * 32
		self.Alarm = 0

class HMI_LS:
	def __init__(self):
		self.Delay = [0] * 32
		self.Alarm = 0

class HMI_LSL:
	def __init__(self):
		self.Delay = [0] * 32
		self.Alarm = 0

class HMI_LSH:
	def __init__(self):
		self.Delay = [0] * 32
		self.Alarm = 0

class HMI_DPIT:
	def __init__(self, SAHH, SAH, SAL, SALL):
		self.SAHH = SAHH
		self.SAH = SAH
		self.SAL = SAL
		self.SALL = SALL
		self.Hty  = 1
		self.AHH  = 0
		self.AH   = 1
		self.AL   = 0
		self.ALL  = 0
		self.Pv = 0

	def set_alarm(self):
		if type(self.Pv) != type('a'):
			self.AHH, self.AH, self.AL, self.ALL = ALM(self.Pv, self.SAHH, self.SAH, self.SAL, self.SALL)

class HMI_PIT:
	def __init__(self, SAHH, SAH, SAL, SALL):
		self.SAHH = SAHH
		self.SAH = SAH
		self.SAL = SAL
		self.SALL = SALL
		self.Hty = 1
		self.AHH = 0
		self.AH = 0
		self.AL = 0
		self.ALL = 0
		self.Pv = 0

	def set_alarm(self):
		if type(self.Pv) != type('a'):
			self.AHH, self.AH, self.AL, self.ALL = ALM(self.Pv, self.SAHH, self.SAH, self.SAL, self.SALL)

class HMI_VSD:
	def __init__(self):
		self.Auto = 1
		self.Reset = 0
		self.Status = 2
		self.Reset_RunHr = 1
		self.Speed_Command = 7710
		self.Permissive = [1] * 32
		self.MSG_Permissive = [1] * 32
		self.MSG_Shutdown = [1] * 32
		self.SD = [0] * 32
		self.Avl = 1
		self.Fault = 0
		self.FTR = 0
		self.FTS = 0
		self.RunHr = 0
		self.Total_RunHr = 0
		self.Speed = 0
		self.Drive_Ready = 0
		self.Shutdown = [0] * 32