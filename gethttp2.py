import urllib2
s = urllib2.urlopen("http://www.aftonbladet.se").read()
t = urllib2.urlopen("http://www.expressen.se").read()
print s[0:20]
print t[0:20]
#print s

