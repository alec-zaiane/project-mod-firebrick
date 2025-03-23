## Node2node communication requirements

### Base level:
- When an external object is created, the receiving node, upon receiving the object, must create a local copy of it
    - If the external copy mentions an object we do not have a copy of, the node should request the object from the node that has it
- When an external object is updated, the receiving node must update its local copy of the object
- When an external object is deleted, the receiving node must delete its local copy of the object
- When a local object is created, the node must broadcast the object to all other nodes
- When a local object is updated, the node must broadcast the update to all other nodes
- When a local object is deleted, the node must broadcast the deletion to all other nodes


