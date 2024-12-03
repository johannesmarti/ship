/*
dragNDropStructure:
    onDragStart: DragItem -> IO
    onDragEnd: IO
    determineDragItem: dragstartEvent -> dragItem
    determineTarget: dragItem * dragoverEvent -> Maybe(target)
    isDroppable: dragItem * target -> Bool

    initialDragArea: dragItem -> dragArea
    dragAreaOfDrop: dropItem * target -> dragArea

    setDraggable: IO
    setDragging: dragArea -> IO
    removeDragging: dragArea -> IO
    highlight: dragItem * target -> IO
    unhighlight: dragItem * target -> IO

    performDromp: dragItem * target-> IO

    target is assumed to implement a reasonable equals
*/

export function attach(structure, element) {
  let dragItem = null;
  let dragging = null;
  let target = null;
    
  structure.setDraggable();

  element.addEventListener('dragstart', (event) => {
    dragItem = structure.determineDragItem(event);
    if (dragItem === null) {
      //console.log("dragstart on unexpected item");
      return;
    }
    structure.onDragStart(dragItem);
    dragging = structure.initialDragArea(dragItem);
    structure.setDragging(dragging);
    console.assert(dragItem !== null, `there is a drag item at end of dragstart`);
    console.assert(dragging !== null, `there is a dragging at end of dragstart`);
  });

  element.addEventListener('dragover', (event) => {
    if (dragItem === null || dragging === null) {
      //console.log("dragover without successfull dragstart");
      return;
    }
    event.preventDefault();

    const newTarget = structure.determineTarget(dragItem, event);
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
      const newDragArea = structure.dragAreaOfDrop(dragItem, target);
      if (!newDragArea.equals(dragging)) {
          structure.removeDragging(dragging);
          dragging = newDragArea;
          structure.setDragging(dragging);
      }
    }
  });

  element.addEventListener('drop', (event) => {
    if (dragItem === null || dragging === null) {
      //console.log("drop without successfull dragstart");
      return;
    }
    if (target !== null) {
      structure.performDrop(dragItem, target)
    }
  });

  element.addEventListener('dragend', (event) => {
    structure.onDragEnd();
    if (target !== null) {
      structure.removeHighlight(dragItem, target);
      target = null;
    }
    if (dragItem !== null) {
      dragItem = null;
    }
    if (dragging !== null) {
      structure.removeDragging(dragging);
      dragging = null;
    }
  });
}
