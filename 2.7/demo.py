from Murmur import MurmurQuery
import time

start = time.time()

murmur = MurmurQuery()
murmur.setup("127.0.0.1", 27800, 1)
murmur.query()

if murmur.is_online():
    print "Online. Users:"
    for user in murmur.users:
        print " ", user["name"]
    print "Total user count: ", len(murmur.users)
else:
    print "Offline."

print "Execution time: ", time.time()-start
