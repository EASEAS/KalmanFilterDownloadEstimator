import socket               # Import module
import os
import time
import math
from random import normalvariate
from matrixClass import matrix

# time between calculations. <=1 every iteration 
delta = 1

##########################################################################
# Model
# Matrices
x = matrix([[0.], [0.]]) # initial state (location and velocity)
P = matrix([[1000., 0.], [0., 1000.]]) # initial uncertainty
u = matrix([[0.], [0.]]) # external motion
F = matrix([[1., delta], [0, 1.]]) # next state function
H = matrix([[1., 0.]]) # measurement function
R = matrix([[1.]]) # measurement uncertainty
I = matrix([[1., 0.], [0., 1.]]) # identity matrix

##########################################################################
# Model
# Estimates
estimate_position = 0.0
estimate_velocity = 0.0


data = []
##########################################################################
# Socket Setup
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                 # Reserve a port for your service.

s.connect(('172.29.36.145', port))
#s.connect((host,port))
s.sendall(b'Hello server!')

#prepare file for sending
f = open('Anaconda.exe','rb')
dat = open('log','w')
totalSize = os.path.getsize("Anaconda.exe")
print('total size: %d' %totalSize)

print('Sending...')
l = f.read(1024)

#begin counting time for real time upload stats
begin = time.time()
start = begin

#initialize loop variables
size = 0		#number of uploaded bytes
dSize = 0		#number of uploaded bytes since last stat print

#begin file upload
while (l):
	s.sendall(l)
	l = f.read(1024)
	#size downloaded
	size += 1024
	#size downloaded since last print
	dSize += 1024

	#kalman measurement. 
	measurement = size

	end = time.time()
	delta = end - start

	#calulate stats after cooldown
	if (delta > 1):
		##################################################################
		# Measurement
		# get measurement
		z = matrix([[measurement]])

		# get difference of measurement and actual value
		y = z - (H*x)

		# measurement with applied covariance + measurement noise
		S = (H * P * H.transpose()) + R

		# calculate gain
		k = P* H.transpose() * S.inverse()

        #update measurement
		x = x +(k*y)
		#update covariance
		P = (I - (k*H))* P

		##################################################################
       	# prediction
		#calculate next state from current + external distrubances
		x = ( F * x ) + u
		#calculate new covariances
		P = F * P * F.transpose() 

		estimate_position = x.value[0][0]
		estimate_velocity = x.value[1][0]

		try:
			print("%d%%" % math.ceil(100*(size/totalSize)) )
			print("Linear est. time left: (%d) \t Kalman est. time(%.4f) \t  Kalman est. time left(%d)" % (math.ceil((totalSize/ dSize) - ( time.time() - begin )),  (totalSize/estimate_velocity), (totalSize/estimate_velocity)- ( time.time() - begin ) ))
		except ZeroDivisionError :
			print("Calculating...")
		#write to data file for post expirement data visualization
		#dat.write(str(time.time() - begin) + ", " + str(math.ceil((totalSize/ dSize) - ( time.time() - begin )))+ ", " + str ( (totalSize/estimate_velocity)- ( time.time() - begin ))+ "\n" ) 
		
		#restart delta timer variables
		start = time.time()
		end = time.time()
		dSize = 0

f.close()
dat.write( str(time.time()-begin))
dat.close()
print ("100%% \nDone Sending: %.2f seconds. Kalman error %.2f" % ((time.time()-begin), ((time.time()-begin) -  (totalSize/estimate_velocity)) ) )
#handshake with server
s.shutdown(socket.SHUT_WR)
s.recv(1024)
s.close()
