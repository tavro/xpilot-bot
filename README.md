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

## Completed tutorials:
- [x] Stationary Targets (2pt)
- [x] Race (2pt)
- [x] Wall Feeler (5pt)
- [x] Distant Targets (2pt)
- [x] Asteroids (4pt)
- [x] Communication (5pt)

## Completed Milestones:
- [x] Basic Movement ```(10pt)``` [SOLVED]
- [x] Path Finding ```(30pt)``` [SOLVED]
- [x] Path Drawing ```(10pt)``` [SOLVED]
- [x] Item Collection ```(15pt)``` [SOLVED]
- [x] Item Handling (Basic) ```(15pt)``` [SOLVED]
- [x] Item Handling (Advanced) ```(15pt)``` [SOLVED]

## Extra Milestones:
- [x] Path following ```(20pt)``` [SOLVED]
- [x] Refuelling ```(15pt)``` [SOLVED]
- [ ] Search and destroy ```(20pt)``` [SKIPPED]

## Custom milestone:
- [x] Multithreading ```(XXpt)```  [SOLVED]

## Bonus points
- Decided by labassistant ```(XXpt)``` 

### Total points so far: ```20```
### Total points so far if we pass: ```150 + multithreading points```
### Total points when solved: ```150 + bonus points```
### Possible points to get so far: ```170```
