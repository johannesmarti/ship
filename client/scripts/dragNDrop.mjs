/*
dragNDropStructure:
    determineDragItem: dragstartEvent -> dragItem
    determineTarget: dragoverEvent -> Maybe(target)
    droppable: dragItem * target -> Bool

    initialDragArea: dragItem -> dragArea
    dragAreaOfDrop: dropItem * target -> dragArea

    setDraggable: IO
    setDragging: dragArea -> IO
    removeDragging: dragArea -> IO
    highlight: dragItem * target -> IO
    unhighlight: dragItem * target -> IO

    performDromp: dragItem * target-> IO
*/

export function attach(structure, element) {
  let dragItem = null;
  let dragging = null;
  let target = null;
    
  structure.setDraggable();

  element.addEventListener('dragstart', (event) => {
    dragItem = structure.determineDragItem(event);
    dragging = structure.initialDragArea(dragItem);
    structure.setDragging(dragging);
    console.assert(dragItem !== null, `there is a drag item at end of dragstart`);
    console.assert(dragging !== null, `there is a dragging at end of dragstart`);
  });

  element.addEventListener('dragover', (event) => {
    console.assert(dragItem !== null, `there is a drag item on dragover event`);
    console.assert(dragging !== null, `there is a dragging on dragover event`);
    // I do not understand why this preventDefault is needed
    event.preventDefault();

    const newTarget = structure.determineTarget(event);
    if (newTarget === null) {
      if (target !== null) {
        structure.removeHighlight(dragItem, target);
        target = null;
      }
      return;
    }
    if (target !== null) {
      if (newTarget.equals(target)) { return; }
      structure.removeHighlight(dragItem, target);
      target = null
    }
    if (structure.isDroppable(dragItem, newTarget)) {
      target = newTarget;
      structure.highlight(dragItem, target);
    }
    const newDragArea = structure.dragAreaOfDrop(dragItem, target);
    if (!newDragArea.equals(dragging)) {
        structure.removeDragging(dragging);
        dragging = newDragAre;
        structure.setDragging(dragging);
    }
  });

  element.addEventListener('drop', (event) => {
    console.assert(dragItem !== null, `there is a drag item on drop event`);
    console.assert(dragging !== null, `there is a dragging on drop event`);

    if (target !== null) {
      structure.performDrop(dragItem, target)
    }
  });

  element.addEventListener('dragend', (event) => {
    if (target !== null) {
      structure.removeHighlight(dragItem, target);
      target = null;
      return;
    }
    if (dragItem !== null) {
      //console.log("dragend without dragItem");
      console.assert(dragging !== null,
          `dragItem and dragging are in sync at dragend`);
      dragItem = null;
      structure.removeDragging(dragging);
      dragging = null;
    }
    console.assert(dragging === null,
        `dragItem and dragging are in sync at dragend`);
  });
}
