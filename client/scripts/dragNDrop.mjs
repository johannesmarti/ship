/*
dragNDropStructure:
    determineDragItem: dragstartEvent -> dragItem
    determineDropSpecification: dragItem * dragoverEvent -> Maybe(dragArea, dropArea, dropItem)

    initialDragArea: dragItem -> dragArea

    setDraggable: IO
    setDragging: dragArea -> IO
    removeDragging: dragArea -> IO
    highlight: dropArea -> IO
    unhighlight: dropArea -> IO
*/

export function attach(structure, element) {
  let dragItem = null;
  let dragging = null;
  let dropItem = null;
  let highlighted = null;
    
  activations.setDraggable();

  element.addEventListener('dragstart', (event) => {
    dragItem = structure.determineDragItem(event);
    dragging = structure.initialDragArea(dragItem));
    activations.setDragging(dragging);
  });

  element.addEventListener('dragover', (event) => {
    console.assert(dragItem !== null,
      `there is a drag item on dragover event`);
    console.assert(dragging !== null,
      `there is a dragging on dragover event`);
    // I do not understand why this preventDefault is needed
    event.preventDefault();

    const dropSpecification =
        structure.determineDropSpecification(dragging, event);
    if (dropSpecification === null) {
      dropItem = null;
      if (highlighted !== null) {
        activiations.removeHighlighting(highlighted);
        highlighted = null;
      }
      return;
    }
    if (!dropSpecification.dragArea.equals(dragging)) {
        activiations.removeDragging(dragging);
        dragging = dropSpecification.dragArea;
        activiations.setDragging(dragging);
    }
    dropItem = dropSpecification.dropItem;
    if (!dropSpecification.dropArea.equals(highlighted)) {
        if (highlighted !== null) {
          activiations.removeHighlighting(highlighted);
          highlighted = dropSpecification.dropArea;
        }
        activiations.addHighlighting(highlighted);
    }
  });

  // TODO: Could try to get rid of duplication in the following two.
  element.addEventListener('drop', (event) => {
    console.assert(dragItem !== null,
      `there is a drag item on drop event`);
    console.assert(dragging !== null,
      `there is a dragging on drop event`);

    dragItem = null;
    activiations.removeDragging(dragging);
    dragging = null;
    if (dropItem !== null) {
      dropItem = null;
      console.assert(hightlighted !== null,
        `dropItem and highlighted not synchronized at drop`);
      activations.removeHighlight(highlighted);
      highlighted = null;
      activations.performDrop(dragItem, dropItem)
      return;
    }
    console.assert(hightlighted === null,
      `dropItem and highlighted not synchronized at drop`);
  });

  element.addEventListener('dragend', (event) => {
    console.assert(dragItem !== null,
      `there is a drag item on dragend event`);
    console.assert(dragging !== null,
      `there is a dragging on dragend event`);

    dragItem = null;
    activiations.removeDragging(dragging);
    dragging = null;
    if (dropItem !== null) {
      // can there be a dragend in which dropItem is not null? why is
      // this the not a drop
      dropItem = null;
      console.assert(hightlighted !== null,
        `dropItem and highlighted not synchronized at dragend`);
      activations.removeHighlight(highlighted);
      highlighted = null;
      return;
    }
    console.assert(hightlighted === null,
      `dropItem and highlighted not synchronized at dragend`);
  });
}
