#! /usr/bin/env python

class file_object:
	
	def __init__(self, filename=None, name_md5=None, name_B64=None, name_type=None, filesize=None, inode=None, parent_inode=None, mode=None, nlink=None, namesize=None, uid=None, gid=None, genId=None, mtime=None, atime=None, ctime=None, crtime=None, xnonce=None, xmaster=None, xNameCipher=None):

		self.filename = filename
		self.name_md5 = name_md5
		self.name_B64 = name_B64
		self.name_type = name_type
		self.filesize = filesize
		self.inode = inode
		self.parent_inode = parent_inode
		self.mode = mode
		self.nlink = nlink
		self.namesize = namesize
		self.uid=uid
		self.gid=gid
		self.genId = genId
		self.mtime = mtime
		self.atime = atime
		self.ctime = ctime
		self.crtime = crtime
		self.xnonce = xnonce
		self.xmaster = xmaster
		self.xNameCipher = xNameCipher

	def __getitem__(self, index):
		if index == "filename":
			return self.filename
		elif index == "name_md5":
			return self.name_md5
		elif index == "name_B64":
			return self.name_B64
		elif index == "name_type":
			return self.name_type
		elif index == "filesize":
			return self.filesize
		elif index == "inode":
			return self.inode
		elif index == "parent_inode":
			return self.parent_inode
		elif index == "mode":
			return self.mode
		elif index == "nlink":
			return self.nlink
		elif index == "namesize":
			return self.namesize
		elif index == "uid":
			return self.uid
		elif index == "gid":
			return self.gid
		elif index == "genId":
			return self.genId
		elif index == "mtime":
			return self.mtime
		elif index == "atime":
			return self.atime
		elif index == "ctime":
			return self.ctime
		elif index == "crtime":
			return self.crtime
		elif index == "xnonce":
			return self.xnonce
		elif index == "xmaster":
			return self.xmaster
		elif index == "xNameCipher":
			return self.xNameCipher
		raise Exception("__getitem__ for index %s not implemented" % index)

