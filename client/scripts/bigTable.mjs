import { Schema } from './schema.mjs';
import { Position, Hierarchization } from './hierarchization.mjs';
import { Virtualizer, TransformedDataView } from './virtualSchema.mjs';
import { attach } from './dragNDrop.mjs';

export function h(tagName, ...args) {
  const el = document.createElement(tagName);
  el.append(...args);
  return el;
}

class MutableHierarchicalIterator {
  constructor(schema, hierarchy) {
    this._schema = schema;
    this._hierarchy = hierarchy;
    this._array = new Array(hierarchy.length).fill(0);
  }

  address() {
    return this._array;
  }

  increment() {
    let k = this._array.length;
    while (k > 0) {
      k--;
      const dimension = this._schema.dimensionAtOrder(this._hierarchy[k]);
      this._array[k]++;
      if (this._array[k] !== dimension.numIndices()) {
        return true;
      }
      this._array[k] = 0;
    }
    return false;
  }

  *freshDigits() {
    let k = this._array.length - 1;
    do {
      yield [k, this._hierarchy[k], this._array[k]];
      if (this._array[k] !== 0) {
        break;
      }
      k--;
    } while (k >= 0);
  }
}

class IndexedPosition {
  constructor(position, index) {
    this._position = position;
    this._index = index;
  }

  static fixed(offset, index) {
    return new IndexedPosition(Position.fixed(offset), index);
  }

  static row(offset, index) {
    return new IndexedPosition(Position.row(offset), index);
  }

  static column(offset, index) {
    return new IndexedPosition(Position.column(offset), index);
  }

  position() { return this._position; }
  index() { return this._index; }
}

class PositionIndex {
  constructor(positionExtractor, fixedLength, rowHierarchyLength, columnHierarchyLength) {
    function arrayOfEmptyArrays(length) {
      return Array(length).fill().map(() => []);
    }
    this._positionExtractor = positionExtractor;
    this._elementToValue = new Map();
    this._fixedArray = arrayOfEmptyArrays(fixedLength);
    this._rowHierarchyArray = arrayOfEmptyArrays(rowHierarchyLength);
    this._columnHierarchyArray = arrayOfEmptyArrays(columnHierarchyLength);
  }

  allElements() {
    return this._elementToValue.keys();
  }

  arrayOfType(type) {
    switch (type) {
      case 'fixed':
        return this._fixedArray;
      case 'rowHierarchy':
        return this._rowHierarchyArray;
      case 'columnHierarchy':
        return this._columnHierarchyArray;
    }
    console.assert(false, `position type should be 'fixed', 'rowHierarchy' or 'columnHierarchy', but is '${type}'`);
  }

  valueOfElement(element) {
    const value = this._elementToValue.get(element);
    return value || null;
  }

  positionOfElement(element) {
    const value = this.valueOfElement(element);
    if (value === null) return null;
    else return this._positionExtractor(value);
  }

  elementsAtPosition(position) {
    const type = position.type();
    const offset = position.offset();
    const array = this.arrayOfType(type);
    console.assert(position.offset() < array.length,
        `HeaderElementindex only has ${array.length} elements in
position ${type}, but got a position with offset '${offset}'`);
    return array[offset];
  }

  add(element, value) {
    this._elementToValue.set(element, value);
    const position = this._positionExtractor(value);
    this.elementsAtPosition(position).push(element);
  }
}

function isHorizontal(type) {
  switch (type) {
    case 'fixed':
      return true;
    case 'rowHierarchy':
      return true;
    case 'columnHierarchy':
      return false;
  }
  console.assert(false, `position type should be 'fixed', 'rowHierarchy' or 'columnHierarchy', but is '${type}'`);
}

export class BigTable {
  constructor(data, arrangement) {
    this._data = data;
    this._arrangement = arrangement;

    localStorage.setItem('arrangement', JSON.stringify(arrangement.toPlainJSON()));
    const baseSchema = data.schema();
    const virtualSchema = arrangement.virtualize(baseSchema);
    this._virtualSchema = virtualSchema;
    this._transformedDataView = new TransformedDataView(data, virtualSchema);
  }

  data() { return this._data }
  arrangement() { return this._arrangement }
  virtualSchema() { return this._virtualSchema }
  transformedDataView() { return this._transformedDataView }

  updateArrangement(newArrangement) {
    return new BigTable(this.data(), newArrangement);
  }

  lookup(rowAddress, columnAddress) {
    const hierarchization = this.arrangement().hierarchization();
    const address = hierarchization.absoluteAddress(rowAddress, columnAddress);
    return this.transformedDataView().lookup(address);
  }

  render() {
    // maybe a lot of the work here should be put into Arrangement
    const schema = this.virtualSchema();
    const arrangement = this.arrangement();
    const hierarchization = arrangement.hierarchization();
    const [rowHierarchy, columnHierarchy] = hierarchization.hierarchies();

    const dragIndex = new PositionIndex(
        (indexedPosition) => indexedPosition.position(),
        hierarchization.fixed().length,
        rowHierarchy.length, columnHierarchy.length);

    const unitIndex = new PositionIndex(
        (position) => position,
        hierarchization.fixed().length === 0 ? 1 : 0,
        rowHierarchy.length === 0 ? 1 : 0,
        columnHierarchy.length === 0 ? 1 : 0);

    let frow;
    let tbody;
    let div = h("div",
        h("table", h("tbody", frow = h("tr"))),
        h("table", tbody = h("tbody"))
    );

    // draw fixed entries
    if (hierarchization.fixed().length === 0) {
      const cell = h("th", "\u2605");
      unitIndex.add(cell, Position.fixed(0));
      frow.append(cell);
    } else {
      for (const [offset, fixedOrder] of hierarchization.fixed().entries()) {
        const order = fixedOrder.order();
        const fixedIndex = fixedOrder.fixedIndex();
        const dimension = schema.dimensionAtOrder(order);
        const cell = h("th", dimension.nameOfIndex(fixedIndex));
        dragIndex.add(cell, IndexedPosition.fixed(offset, fixedIndex));
        frow.append(cell);
      }
    }

    // using arrow function to get the right behavior of 'this'
    const createHeaderCell = (order, dimension, index) => {
      const cell = h("th", dimension.nameOfIndex(index));
      cell.addEventListener('click', () => {
        const baseSchema = this.data().schema();
        const baseDimension = baseSchema.dimensionAtOrder(order);
        const baseIndex = dimension.transform(index);
        const virtualizer = this.arrangement().virtualizer();
        const newVirtualizer =
            virtualizer.update(order, baseIndex, baseDimension);
        const newArrangement = arrangement.updateVirtualizer(newVirtualizer);
        div.replaceWith(this.updateArrangement(newArrangement).render());
      });
      return cell;
    }

    const rowLength = Math.max(1, rowHierarchy.length);
    const columnLength = Math.max(1, columnHierarchy.length);
    // draw column headings
    {
      const rowArray = new Array(columnLength);
      for (let o = 0; o < rowArray.length; o++) {
        const row = h("tr");
        rowArray[o] = row;
        tbody.append(row);
      }
      // generate top left cell:
      {
        const cell = h("td")
        cell.colSpan = rowLength;
        cell.rowSpan = columnLength;
        rowArray[0].append(cell);
      }
      if (columnHierarchy.length === 0) {
        const cell = h("th", "\u2605");
        unitIndex.add(cell, Position.column(0));
        rowArray[0].append(cell);
      } else {
        // go through all cells and draw their heading
        const columnIterator = new MutableHierarchicalIterator(schema, columnHierarchy);
        do {
          const row = h("tr");
          // draw row heading
          let multiplier = 1;
          for (let [k, order, index] of columnIterator.freshDigits()) {
            const dimension = schema.dimensionAtOrder(order);
            const cell = createHeaderCell(order, dimension, index);
            cell.colSpan = multiplier;
            dragIndex.add(cell, IndexedPosition.column(k, index));
            rowArray[k].append(cell);
            multiplier *= dimension.numIndices();
          }
        } while (columnIterator.increment());
      }
    }

    const drawDataPartOfRow = (row, rowAddress) => {
      const columnIterator = new MutableHierarchicalIterator(schema, columnHierarchy);
      do {
        const value = this.lookup(rowAddress, columnIterator.address());
        row.append(h("td", value.toFixed(3)));
      } while(columnIterator.increment());
    }

    // draw data rows with iterator
    if (rowHierarchy.length === 0) {
        const row = h("tr");
        const cell = h("th", "\u2605");
        unitIndex.add(cell, Position.row(0));
        row.append(cell);
        drawDataPartOfRow(row, []);
        tbody.append(row);
    } else {
      const rowIterator = new MutableHierarchicalIterator(schema, rowHierarchy);
      do {
        const row = h("tr");
        // draw row heading
        let multiplier = 1;
        for (let [k, order, index] of rowIterator.freshDigits()) {
          const dimension = schema.dimensionAtOrder(order);
          const cell = createHeaderCell(order, dimension, index);
          cell.rowSpan = multiplier;
          dragIndex.add(cell, IndexedPosition.row(k, index));
          row.prepend(cell);
          multiplier *= dimension.numIndices();
        }
        drawDataPartOfRow(row, rowIterator.address());
        tbody.append(row);
      } while (rowIterator.increment());
    }
    this.addDragNDrop(dragIndex, unitIndex, div);
    return div;
  }

  // maybe these should only be attached at the next render
  addDragNDrop(dragIndex, unitIndex, div) {
    const arrangement = this.arrangement();
    const hierarchization = arrangement.hierarchization();

    class DimensionDropTarget {
      constructor(position) {
        this._position = position;
      }

      position() { return this._position; }

      equals(other) {
        return other instanceof DimensionDropTarget &&
               this.position().equals(other.position());
      }
    }

    class IndexDropTarget {
      constructor(index) {
        this._index = index;
      }

      index() { return this._index; }

      equals(other) {
        return other instanceof IndexDropTarget &&
               this.index() === other.index();
      }
    }

    function determineHorizontalOffset(event, rectangle) {
      const xOffset = event.clientX - rectangle.left;
      return xOffset < rectangle.width / 2 ? 0 : 1;
    }

    function determineVerticalOffset(event, rectangle) {
      const yOffset = event.clientY - rectangle.top;
      return yOffset < rectangle.height / 2 ? 0 : 1;
    }
    
    function determineDropTarget(dragPosition, event) {
      const target = event.target.closest('th');
      if (target === null) { return null; }
      const overIndexedPosition = dragIndex.valueOfElement(target);
      if (overIndexedPosition === null) { 
        const unitPosition = unitIndex.positionOfElement(target);
        if (unitPosition === null) return null;
        else return new DimensionDropTarget(unitPosition);
      }

      const boundingRectangle = target.getBoundingClientRect();
      const overPosition = overIndexedPosition.position();
      if (overPosition.equals(dragPosition)) {
        switch (overPosition.type()) {
          case 'fixed': return null
          case 'rowHierarchy':
            return new IndexDropTarget(overIndexedPosition.index() +
                        determineVerticalOffset(event, boundingRectangle));
          case 'columnHierarchy':
            return new IndexDropTarget(overIndexedPosition.index() +
                        determineHorizontalOffset(event, boundingRectangle));
        }
      }
      const offset = isHorizontal(overPosition.type()) ?
                        determineHorizontalOffset(event, boundingRectangle) :
                        determineVerticalOffset(event, boundingRectangle);
      const dropPosition = new Position(overPosition.type(),
                                        overPosition.offset() + offset);
      return new DimensionDropTarget(dropPosition);
    }

    function operationOnPosition(operationName, position) {
      if (hierarchization.isPosition(position)) {
        if (isHorizontal(position.type())) {
          for (const cell of dragIndex.elementsAtPosition(position)) {
            cell.classList[operationName]('dragover-left');
          }
        } else {
          for (const cell of dragIndex.elementsAtPosition(position)) {
            cell.classList[operationName]('dragover-top');
          }
        }
      } else if (hierarchization.isDropPosition(position)) {
        const type = position.type();
        const offset = position.offset();
        if (offset === 0) { // we are a unitPosition
          for (const cell of unitIndex.elementsAtPosition(position)) {
            cell.classList[operationName]('dragover-unit');
          }
        } else { // we are a dragPosition
          const mutating = new Position(type, offset - 1);
          if (isHorizontal(type)) {
            for (const cell of dragIndex.elementsAtPosition(mutating)) {
              cell.classList[operationName]('dragover-right');
            }
          } else {
            for (const cell of dragIndex.elementsAtPosition(mutating)) {
              cell.classList[operationName]('dragover-bottom');
            }
          }
        }
      } else {
        console.assert(false, `highlighting on invalid position: ${position}`);
      }
    }

    const dragNDropStructure = {
      setDraggable: () => {
        for (let cell of dragIndex.allElements()) {
          cell.setAttribute('draggable', 'true');
        } 
      },

      determineDragItem: (event) => {
        return dragIndex.valueOfElement(event.target);
      },

      initialDragArea: (indexedPosition) => {
        return indexedPosition.position();
      },

      setDragging: (position) => {
        for (const cell of dragIndex.elementsAtPosition(position)) {
          cell.classList.add('dragging');
        }
      },

      removeDragging: (position) => {
        for (const cell of dragIndex.elementsAtPosition(position)) {
          cell.classList.remove('dragging');
        }
      },

      determineTarget: (indexedPosition, event) => {
        return determineDropTarget(indexedPosition.position(), event);
      },

      isDroppable: (indexedPosition, target) => {
        return target instanceof DimensionDropTarget &&
               hierarchization.isMovable(indexedPosition.position(), target.position())
      },

      performDrop: (indexedPosition, target) => {
        const newHierarchization = hierarchization.move(
            indexedPosition.position(),
            target.position(),
            indexedPosition.index());
        const newArrangement = arrangement.updateHierarchization(newHierarchization);
        div.replaceWith(this.updateArrangement(newArrangement).render());
      },

      dragAreaOfDrop: (indexedPosition, target) => {
        return indexedPosition.position();
      },

      highlight: (indexedPosition, target) => {
        operationOnPosition('add', target.position());
      },

      removeHighlight: (indexedPosition, target) => {
        operationOnPosition('remove', target.position());
      }
    }

    attach(dragNDropStructure, div);
  }
}
