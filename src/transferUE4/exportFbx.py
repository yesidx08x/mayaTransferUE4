#!/usr/bin/python
#coding=utf-8
import maya.cmds as mc
import maya.mel as mel
import os,json
import tempfile

try:
	mel.eval("loadPlugin fbxmaya;")
except RuntimeError:
	mc.confirmDialog(title="Error",button="Yes",icon="error",
	message="没有正常挂载FBX插件!") 

class exportBy():
	def __init__(self,parent=None):
		return

	def exportfbx(self,args=[]):
		self.chr_path_name =''
		ue4cmd,ue4proj,mayafile,fbxfile,ue4path,export_options,assettype,self.exportEleL = args
		print(ue4cmd,ue4proj,mayafile,fbxfile,ue4path,export_options,assettype,self.exportEleL)
		self.projectname = os.path.basename(mayafile).split("_")[0] #SYYX_ep000_sc001_sh029_ani_v001.ma
		ext = mayafile.split(".")[-1].lower()
		if ext in ["mb","ma"]:
			self.openMayaFile(mayafile=mayafile,ext=ext)
		elif ext == "fbx":
			self.importFbxFile(xfile=mayafile)
		else:
			print(u">>>Error: 不是有效的文件类型！")
			return None
		#[onlyAni,withConstraint,scaleFactor,exportShape,smoothGroup,smoothMesh,upAxis]
		if assettype == 'asset':
			if self.exportEleL[0]:
				reslut,Info = self.exportFbxFile(objfile=fbxfile,asset_type='asset',options=self.optionsArgs(kind='model'))
				if not reslut:
					return None
				basename = os.path.basename(fbxfile)
				self.asset_name = mayafile.split("_")[2] #SYYX_chr_LinY_mod_v002.mb
				newfile = os.path.join(ue4path,self.asset_name+'.fbx')
				isCopy = self.copyFbxFile(oldfile=fbxfile,xfile=newfile)
				if os.path.isfile(newfile):
					if export_options[1] or export_options[2]:
						tmp_pyfile = tempfile.NamedTemporaryFile().name+".py"
						#ue4cmd ,ue_path, tmp_pyfile, fbxpath, newline,asset_type
						args = [ue4cmd ,ue4proj,ue4path, tmp_pyfile,fbxfile, newfile,assettype]
						self.runUE4cmd(args)
						if export_options[2]:
							return
		elif assettype == 'shot':
			fbxDict = self.listMayaScnD()
			joints=[]
			cameras = []
			for n in fbxDict['dynamic'].keys():
				joints.append(fbxDict['dynamic'][n]['joint'])
			for n in fbxDict['camera'].keys():
				joints.append(fbxDict['camera'][n]['name'])
			self.bakeAni(joints = joints,cameras = cameras)
			if self.exportEleL[0]:
				for value in fbxDict['camera'].values():
					#value['name'],value['fbx'],value['kind']
					mc.select(cl=True)
					mc.select(mc.ls(value['name'],type='transform'))
					fbxfile = os.path.join(ue4path,value['fbx']).replace('\\','/')
					print('>>>shot camera :',fbxfile,value)
					self.start_frame = value['start']
					self.end_frame = value['end']
					self.start_f = int(self.start_frame) - 5
					self.end_f = int(self.end_frame) + 3
					reslut,Info = self.exportFbxFile(objfile=fbxfile,asset_type='shot',options=self.optionsArgs(kind='camera'))
					if not reslut:
						return None
					newfile = os.path.join(ue4path,value['fbx'])
					self.asset_name = value['name']
					if export_options[1] or export_options[2]:
						tmp_pyfile = tempfile.NamedTemporaryFile().name+".py"
						#ue4cmd ,ue_path, tmp_pyfile, fbxpath, newline,asset_type
						args = [ue4cmd ,ue4proj,ue4path, tmp_pyfile,fbxfile, newfile,'camera']
						self.runUE4cmd(args)
						if export_options[2]:
							return
			if self.exportEleL[1]:
				for value in fbxDict['dynamic'].values():
					mc.select(cl=True)
					mc.select(mc.ls(value['model'],type='transform'))
					mc.select(mc.ls(value['joint'],type='transform'),add=True)
					fbxfile = os.path.join(ue4path,value['fbx']).replace('\\','/')
					print('>>>shot character :',fbxfile,value)
					self.chr_path_name = value['name'].split(':')[0]
					reslut,Info = self.exportFbxFile(objfile=fbxfile,asset_type='shot',options=self.optionsArgs(kind='character'))
					if not reslut:
						return None
					newfile = os.path.join(ue4path,value['fbx'])
					self.asset_name =value['name'].split('_')[2]
					if export_options[1] or export_options[2]:
						tmp_pyfile = tempfile.NamedTemporaryFile().name+".py"
						#ue4cmd ,ue_path, tmp_pyfile, fbxpath, newline,asset_type
						args = [ue4cmd ,ue4proj,ue4path, tmp_pyfile,fbxfile, newfile,assettype]
						self.runUE4cmd(args)
						if export_options[2]:
							return
		
		return

	def bakeAni(self,joints=[],cameras=[]):
		mc.playbackOptions(e=1, min=self.start_f, ast=self.start_f, aet=self.end_f, max=self.end_f)
		bs_node = mc.ls(type='blendShape')

		bake_nodes = joints
		for cam in cameras:
			bake_nodes.append(cam)
		bake_nodes.extend(bs_node)

		mc.bakeResults(bake_nodes, time=(self.start_f, self.end_f), sampleBy=1, simulation=1, oversamplingRate=1,
					hierarchy='below', preserveOutsideKeys=1, sparseAnimCurveBake=0, removeBakedAttributeFromLayer=0,
					removeBakedAnimFromLayer=0, bakeOnOverrideLayer=0, minimizeRotation=1, controlPoints=0, shape=1,
					disableImplicitControl=1)
		return

	def optionsArgs(self,kind=''):
		optionStrL=[]
		if kind=='camera':
			optionStrL.append('FBXExportAnimationOnly -v false;')
			optionStrL.append('FBXExportApplyConstantKeyReducer -v false;')
			optionStrL.append('FBXExportBakeComplexAnimation -v true;')
			optionStrL.append('FBXExportBakeComplexStart -v {0};'.format(self.start_f))
			optionStrL.append('FBXExportBakeComplexEnd -v {0};'.format(self.end_f))
			optionStrL.append('FBXExportBakeComplexStep -v 1;')
			optionStrL.append('FBXExportBakeResampleAnimation -v false;')
			optionStrL.append('FBXExportCacheFile -v 0;')
			optionStrL.append('FBXExportCameras -v 1;')
			optionStrL.append('FBXExportConstraints -v 0;')
			optionStrL.append('FBXExportSkeletonDefinitions -v 0;')
			optionStrL.append('FBXExportSkins -v 1;')
			optionStrL.append('FBXExportShapes -v 1;')
			optionStrL.append('FBXExportSmoothingGroups -v 1;')
			optionStrL.append('FBXExportSmoothMesh -v 1;')
			# cmd+= 'FBXExportSplitAnimationIntoTakes -v 0;\n'
			optionStrL.append( 'FBXExportTangents -v 0;')
			optionStrL.append('FBXExportTriangulate -v 0;')
			# cmd+= 'FBXExportUpAxis -v \"y\";\n'
			optionStrL.append('FBXExportUseSceneName -v 0;')

		if kind == 'model':
			optionStrL.append('FBXExportAnimationOnly -v false;')	
			optionStrL.append('FBXExportConstraints -v {0};'.format('true'))
			optionStrL.append('FBXExportScaleFactor {0};'.format(1))
			optionStrL.append('FBXExportShapes -v {0};'.format('true'))#"true"
			optionStrL.append('FBXExportSmoothingGroups -v {0};'.format('true'))#"true"
			optionStrL.append('FBXExportSmoothMesh -v {0};'.format('true'))#"true"
			#upAxis = "FBXExportUpAxis {0};".format(options[6])#"y""z"
				
		if kind =='character':
			#cmds.select(ns + ':' + mod_grp, ns + ':Root', r=1)
			optionStrL.append('FBXExportAnimationOnly -v false;')
			optionStrL.append('FBXExportApplyConstantKeyReducer -v false;')
			optionStrL.append('FBXExportBakeComplexAnimation -v true;')
			optionStrL.append('FBXExportBakeComplexStart -v {0};'.format(self.start_f))
			optionStrL.append('FBXExportBakeComplexEnd -v {0};'.format(self.end_f))
			optionStrL.append('FBXExportBakeComplexStep -v 1;')
			optionStrL.append('FBXExportBakeResampleAnimation -v false;')
			optionStrL.append('FBXExportCacheFile -v 0;')
			optionStrL.append('FBXExportCameras -v 0;')
			optionStrL.append('FBXExportConstraints -v 0;')
			optionStrL.append('FBXExportSkeletonDefinitions -v 0;')
			optionStrL.append('FBXExportSkins -v 1;')
			optionStrL.append('FBXExportShapes -v 1;')
			optionStrL.append('FBXExportSmoothingGroups -v 1;')
			optionStrL.append('FBXExportSmoothMesh -v 1;')
			#optionStrL.append('FBXExportScaleFactor 1.0;')
			# cmd+= 'FBXExportSplitAnimationIntoTakes -v 0;\n'
			optionStrL.append('FBXExportTangents -v 0;')
			optionStrL.append('FBXExportTriangulate -v 0;')
			#optionStrL.append('FBXExportUpAxis y;')
			# cmd+= 'FBXExportUpAxis -v \"y\";\n'
			optionStrL.append('FBXExportUseSceneName -v 0;')

		return optionStrL

	def openMayaFile(self,mayafile="",ext="mb"):
		if ext=="ma":
			mayatype="mayaAscii"
		elif ext=="mb":
			mayatype="mayaBinary"
		try:
			mc.file(mayafile, open=True, type=mayatype,force=True)
		except Exception as ex:
			return False
		return

	def copyFbxFile(self,oldfile="",xfile=""):
		import shutil
		try:
			if not os.path.isdir(os.path.dirname(xfile)):
				os.makedirs(os.path.dirname(xfile))
			reslut = shutil.copy(oldfile,xfile)
			return True
		except Exception  as ex:
			print(ex)
			return False

	def importFbxFile(self,xfile=""):
		mc.file( f=True, new=True)
		mc.currentUnit(time="pal")
		mel.eval("FBXImportMode -v add;")
		#mel.eval("FBXImport -f "{0}";".format(fbxfile[1]))
		try:
			mc.file(xfile,i=True,type="FBX",ignoreVersion=True)
			return True
		except:
			print(u">>>ERROR: import fbx file failed -- {0}".format(xfile))
			return False

	# 根据类型导出不同的fbx转成uasset
	def exportFbxFile(self,objfile="",asset_type='asset',options=[]):
		if asset_type=='asset':
			meltext = "FBXExport -f \"{0}\" ;".format(objfile) #-s
		elif asset_type == 'shot':
			meltext = "FBXExport -f \"{0}\" -s;".format(objfile) #-s
		
		#onlyAni = "FBXExportAnimationOnly -v {0};".format(options[0])#"false"
		#withConstraint = "FBXExportConstraints -v {0};".format(options[1])#"true"
		#scaleFactor = "FBXExportScaleFactor {0};".format(options[2])#0.1
		#exportShape = "FBXExportShapes -v {0};".format(options[3])#"true"
		#smoothGroup = "FBXExportSmoothingGroups -v {0};".format(options[4])#"true"
		#smoothMesh = "FBXExportSmoothMesh -v {0};".format(options[5])#"true"
		#upAxis = "FBXExportUpAxis {0};".format(options[6])#"y""z"

		#scriptStrL = [onlyAni,withConstraint,scaleFactor,exportShape,smoothGroup,smoothMesh,upAxis,meltext]
		scriptStrL = options
		scriptStrL.append(meltext)
		print(scriptStrL)
		try:
			for line in scriptStrL:
				reslut = mel.eval(line)
			return True,reslut
		except Exception as ex:
			print(u">>>ERROR: 导出fbx失败！{0}".format(ex))
			return False,str(ex)
		return

	def runUE4cmd(self,args):
		import re
		#key,fbxfile,avatar_name,uepath,newline,asset_type = args
		ue4cmd ,ue4proj,ue_path, tmp_pyfile, fbxpath, newline,assettype = args
		py_file = os.path.dirname(__file__) + "/uassetConvert.py"
		print(py_file)
		args=self.getArgs(self.asset_name,ue_path,fbxpath)
		tmp_pyfile = self.newUassetPy(assettype,py_file,args)
		basename = os.path.basename(tmp_pyfile)
		cmdtext = "\"{0}\" \"{1}\" -ExecutePythonScript=\"{2}\"".format(ue4cmd ,ue4proj, tmp_pyfile)
		print('cmdtext:',cmdtext)
		cmdfile = '{0}_{1}.{2}'.format(fbxpath[:-4],basename[:-3],"cmd")
		cmdfile = re.sub("[^a-z^A-Z^0-9^/^:^.^_]", "", cmdfile)
		print(cmdfile)
		f=open(cmdfile,"w")
		f.writelines(["#"+newline+"\n",cmdtext])
		f.close()
		from threading import Thread
		nthrd = Thread(target=self.cmdOut, args=(cmdfile,))
		nthrd.daemon=True
		nthrd.start()
		return

	def getArgs(self,avatar_name,ue_path,fbxpath):
		asset_name = avatar_name
		xpath = os.path.dirname(fbxpath)
		if not os.path.isdir(xpath):
			os.makedirs(xpath)
		iclone_folder = xpath.replace("\\","/").split("/")[-1] #"icloneFBX"
		project_path = ue_path.replace("\\","/")
		game_sequence = "/Game/Sequences"
		game_rlcontent ="/Game/RLContent"
		args = asset_name, iclone_folder, project_path, game_sequence, game_rlcontent
		return args

	def cmdOut(self,cmdfile):
		import sys
		if sys.version_info[0]>2:
			import subprocess
			subprocess.run(cmdfile,shell=False)
		else:
			os.system(cmdfile)

	def listMayaScnD(self):
		fbxDict = {'dynamic':{},'camera':{}}
		#mc.ls('SYYX_*:Main',typ='transform')
		objrule = '{0}_*:Main'.format(self.projectname)
		camrule = '{0}_*'.format(self.projectname)
		objL = mc.ls(objrule,type='transform')
		camL = mc.ls(camrule,type='camera')
		n=0
		for cam in camL:
			camT = mc.listRelatives(cam, p=1)[0]
			fbxfile = '{0}.fbx'.format(camT)
			self.start_frame = camT.split('_')[4]
			self.end_frame = camT.split('_')[5]
			self.start_f = int(self.start_frame) - 5
			self.end_f = int(self.end_frame) + 3
			fbxDict['camera'][n]={'name':camT,'kind':'camera', 'fbx':fbxfile,'start':self.start_frame,'end':self.end_frame}
			n+=1
		m=0
		for obj in objL:
			fbxfile = '{0}.fbx'.format(obj.split('_')[2])
			chr=obj.split('_')[2]
			# 这里要操作导出的不是Main组，是下面的model组，名称是资产名
			modelgrp = mc.ls('{0}:{1}'.format(obj.split(':')[0],chr),type='transform')[0]
			joint = None
			if not mc.ls(obj.replace(':Main',':Root'))==[]:
				joint = obj.replace(':Main',':Root')
			fbxDict['dynamic'][n]={'name':obj, 'model':modelgrp,'kind':obj.split('_')[1],'fbx':fbxfile,'joint':joint}
		return fbxDict

	def newUassetPy(self,assettype,pypath,args):
		asset_name, iclone_folder, project_path, game_sequence, game_rlcontent = args
		#print(pypath)
		f = open(pypath,'r')
		orinL = f.readlines()
		f.close()
		if assettype == 'shot':
			newVarL = ["import os,re\n",
			"import unreal\n",
			"asset_name = '{0}'\n".format(asset_name),
			"chr_path_name = '{0}'\n".format(self.chr_path_name),
			"new_name = re.sub(r'[_.)]','',asset_name).replace('(','_')\n"
			"iclone_folder = '{0}'\n".format(iclone_folder),
			"project_path = '{0}'\n".format(project_path),
			"fbx_name = '{0}.fbx'.format(asset_name)\n",
			"_FBX_file = '{0}/{1}'.format(project_path,fbx_name)\n",
			"game_sequence = '{0}'\n".format(game_sequence),
			"game_rlcontent = '{0}'\n".format(game_rlcontent),
			"sequence_path = '{0}/MyLevelSequence'.format(game_sequence)\n",
			"actor_path = '{0}/{1}/{1}'.format(game_rlcontent, new_name)\n",
			"animation_path = '/Game/{0}/{1}'.format(iclone_folder, asset_name.replace('.','_').replace('(','_').replace(')','_'))\n",
			"_skeleton_path = '{0}/{1}/{2}_{1}Hi_Skeleton'.format(game_rlcontent,new_name,chr_path_name)\n"]
			endExecL = ["\n    option = buildAnimationImportOptions(_skeleton_path)\n",
			"    animation_task = buildImportTask(file_name=_FBX_file, destinataion_path='/Game/{0}', options=option)\n".format(iclone_folder),
			"    executeImportTasks([animation_task])\n"]
		elif assettype == 'asset':
			newVarL = ["import os,re\n",
			"import unreal\n",
			"asset_name = '{0}'\n".format(asset_name),
			"exportEleL = [{0},{1},{2}]\n".format(self.exportEleL[0],self.exportEleL[1],self.exportEleL[2]),
			"new_name = re.sub(r'[.)]','',asset_name).replace('(','_')\n"
			"iclone_folder = '{0}'\n".format(iclone_folder),
			"project_path = '{0}'\n".format(project_path),
			"fbx_name = '{0}.fbx'.format(asset_name)\n",
			"_FBX_file = '{0}/{1}'.format(project_path,fbx_name)\n",
			"game_sequence = '{0}'\n".format(game_sequence),
			"game_rlcontent = '{0}'\n".format(game_rlcontent),
			"sequence_path = '{0}/MyLevelSequence'.format(game_sequence)\n",
			"actor_path = '{0}/{1}/{1}'.format(game_rlcontent, new_name)\n",
			"animation_path = '/Game/{0}/{1}'.format(iclone_folder, asset_name.replace('.','_').replace('(','_').replace(')','_'))\n",
			"_skeleton_path = '{0}/{1}/{1}_Skeleton'.format(game_rlcontent,new_name)\n"]
			endExecL = ["\n    importMyAssets(exportEleL)\n"]
		elif assettype == 'camera':
			newVarL = ["import os,re\n",
			"import unreal\n",
			"asset_name = '{0}'\n".format(asset_name),
			"new_name = re.sub(r'[.)]','',asset_name).replace('(','_')\n"
			"iclone_folder = '{0}'\n".format(iclone_folder),
			"project_path = '{0}'\n".format(project_path),
			"fbx_name = '{0}.fbx'.format(asset_name)\n",
			"_FBX_file = '{0}/{1}'.format(project_path,fbx_name)\n",
			"game_sequence = '{0}'\n".format(game_sequence),
			"game_rlcontent = '{0}'\n".format(game_rlcontent),
			"sequence_path = '{0}/MyLevelSequence'.format(game_sequence)\n",
			"actor_path = '{0}/{1}/{1}'.format(game_rlcontent, new_name)\n",
			"animation_path = '/Game/{0}/{1}'.format(iclone_folder, asset_name.replace('.','_').replace('(','_').replace(')','_'))\n",
			"_skeleton_path = '{0}/{1}/{1}_Skeleton'.format(game_rlcontent,new_name)\n"]
			endExecL = ["\n    importCamera(sequence=sequence_path, import_filename=_FBX_file) #camera import\n"]
		newVarL.extend(orinL[14:])
		newVarL.extend(endExecL)

		tmp_pyfile = tempfile.NamedTemporaryFile().name+".py"
		with open(tmp_pyfile,'w') as f:
			f.writelines(newVarL)
			f.flush()
			f.close()
		return tmp_pyfile

	def __main__(self):
		return