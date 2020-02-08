# X-Pilot AI Project

 ========================================================

 BOTNAME.pdf a bot for completing various tasks in XPILOT

 Written by: isaho220, trugr925, andfr210
 Updated: DEC 16, 20:05

 Features: BASIC NAVIGATION, ITEM-COLLECTION AND HANDLING,
 PATH-FINDING FOLLOWING DRAWING AND OPTIMIZATION,
 REFUELLING, SEARCH AND DESTROY, MULTITHREADING

 BASIC NAVIGATION:
 Moves to specified (x, y) coord
 Use by writing following in chat:

 move-to-stop x y :[botname] (this will stop at specified coord)

 move-to-pass x y :[botname] (this will pass by specified coord)

 move-to-pos  x y :[botname] (this will do the same as pass)

 ITEM-COLLECTION:
 Collects specified item
 Use by writing following in chat:

 collect-item item :[botname]

 ITEM-HANDLING:
 Uses specified item at (x, y) coord
 Use by writing following in chat:

 use-item item x y :[botname]
 use-item tank x y (next/prev/detach/fuel) :[botname]

 PATH-HANDLING:
 Returns safe and optimized a* path from
 startPos (y, x) to endPos (y, x)
 Draws finished path as well as map in console when done

 REFUELLING: 
 Moves to specified fuelstation and refuels ship
 Use by writing following in chat:

 refuel stationId :[botname]

 SEARCH AND DESTROY:
 More like 'flee'

 MULTITHREADING:
 Runs a* code on other thread

 FOR TESTING:

 REFUELLING,       MAP : fuel.xp

 BASIC NAVIGATION, MAP : astar.xp   

 PATH HANDLING,    MAP : astar.xp   

 ITEM COLLECTION,  MAP : item.xp

 ITEM HANDLING,    MAP : item.xp
 
 MULTITHREADING,   MAP : random

 ========================================================
