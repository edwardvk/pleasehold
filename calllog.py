# -*- coding: utf-8 -*-
"""
Created on 2012-07-07 14:37:28.193885

@author: edward@nitric.co.za
"""
import MySQLdb

def calllog(telephoneid, number, duration, state):
	conn = MySQLdb.connect(host="localhost",user="root",passwd="AZXCDxx",db="strand")
	cursor = conn.cursor()	
	cursor.execute("""
		INSERT INTO calllog (telephoneid, number, date, duration, state) VALUES ('%s', '%s', NOW(),'%s', '%s')""" %
			(telephoneid,number,duration,state))	
	cursor.close ()
	conn.close ()

if __name__ == "__main__":
	calllog(1,1,1,1)