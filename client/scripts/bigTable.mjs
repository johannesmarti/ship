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

  equals(otherIndexedPosition) {
    return this.index() == otherIndexedPosition.index() &&
           this.position().equals(otherIndexedPosition.position());
  }
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

function showsHorizontal(type) {
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

class DimensionDragArea {
  constructor(position) {
    this._position = position;
  }

  position() { return this._position; }

  equals(other) {
    return other instanceof DimensionDragArea &&
           this.position().equals(other.position());
  }

  accept(visitor) { return visitor.visitDimensionDragArea(this.position()); }
}

class IndexDragArea {
  constructor(indexedPosition) {
    this._indexedPosition = indexedPosition;
  }

  indexedPosition() { return this._indexedPosition; }

  equals(other) {
    return other instanceof IndexDragArea &&
           this.indexedPosition().equals(other.indexedPosition());
  }

  accept(visitor) { return visitor.visitIndexDragArea(this.indexedPosition()); }
}

class DimensionDropTarget {
  constructor(position) {
    this._position = position;
  }

  position() { return this._position; }

  equals(other) {
    return other instanceof DimensionDropTarget &&
           this.position().equals(other.position());
  }

  accept(visitor) {
    return visitor.visitDimensionDropTarget(this.position());
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

  accept(visitor) {
    return visitor.visitIndexDropTarget(this.index());
  }
}

class BinDropTarget {
  equals(other) { return other instanceof BinDropTarget; }

  accept(visitor) { return visitor.visitBinDropTarget(); }
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
    const star = "\u2605";
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
      const cell = h("th", star);
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
    let binElement;
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
        binElement = h("th", "BIN");
        binElement.classList.add('hidden');
        binElement.classList.add('bin-element');
        binElement.colSpan = rowLength;
        binElement.rowSpan = columnLength;
        rowArray[0].append(binElement);
      }
      if (columnHierarchy.length === 0) {
        const cell = h("th", star);
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
            cell.classList.add('soft');
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
        const cell = h("th", star);
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
    this.addDragNDrop(dragIndex, unitIndex, binElement, div);
    return div;
  }

  // maybe these should only be attached at the next render
  addDragNDrop(dragIndex, unitIndex, binElement, div) {
    const arrangement = this.arrangement();
    const hierarchization = arrangement.hierarchization();
    const virtualizer = arrangement.virtualizer();
    const bigTable = this;
    const virtualSchema = this.virtualSchema();

    // Maybe indexedPositions make only sense for drag elements that are
    // not fixed and thus come from one of the hierarchies.
    function *elementsAtIndexedPosition(indexedPosition) {
      const position = indexedPosition.position();
      const elementsAtPosition = dragIndex.elementsAtPosition(position);
      const order = hierarchization.orderOfPosition(position);
      const sizeOfDimension = virtualSchema.dimensionAtOrder(order).numIndices();
      const index = indexedPosition.index();

      for (let o = index; o < elementsAtPosition.length; o += sizeOfDimension) {
        yield elementsAtPosition[o];
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
      if (target === binElement) { return new BinDropTarget(); }
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
      const offset = showsHorizontal(overPosition.type()) ?
                        determineHorizontalOffset(event, boundingRectangle) :
                        determineVerticalOffset(event, boundingRectangle);
      const dropPosition = new Position(overPosition.type(),
                                        overPosition.offset() + offset);
      return new DimensionDropTarget(dropPosition);
    }

    // TODO: Could make this nicer:
    function operationOnPosition(operationName, position) {
      const type = position.type();
      const offset = position.offset();
      const length = hierarchization.arrayOfType(type).length;
      if (offset === 0) {
        if (length === 0) {
          for (const cell of unitIndex.elementsAtPosition(position)) {
            cell.classList[operationName]('dragover-unit');
          }
        } else {
          if (showsHorizontal(type)) {
            for (const cell of dragIndex.elementsAtPosition(position)) {
              cell.classList[operationName]('dragover-left');
            }
          } else {
            for (const cell of dragIndex.elementsAtPosition(position)) {
              cell.classList[operationName]('dragover-top');
            }
          }
        }
      } else {
        const before = new Position(type, offset - 1);
        if (position.offset() === length) {
          if (showsHorizontal(type)) {
            for (const cell of dragIndex.elementsAtPosition(before)) {
              cell.classList[operationName]('dragover-right');
            }
          } else {
            for (const cell of dragIndex.elementsAtPosition(before)) {
              cell.classList[operationName]('dragover-bottom');
            }
          }
        } else {
          if (showsHorizontal(type)) {
            for (const cell of dragIndex.elementsAtPosition(before)) {
              cell.classList[operationName]('dragover-thin-right');
            }
            for (const cell of dragIndex.elementsAtPosition(position)) {
              cell.classList[operationName]('dragover-thin-left');
            }
          } else {
            for (const cell of dragIndex.elementsAtPosition(before)) {
              cell.classList[operationName]('dragover-thin-bottom');
            }
            for (const cell of dragIndex.elementsAtPosition(position)) {
              cell.classList[operationName]('dragover-thin-top');
            }
          }
        }
      }
    }

    function operationOnIndexedPosition(operationName, indexedPosition) {
      const position = indexedPosition.position();
      const order = hierarchization.orderOfPosition(position);
      const lengthOfOrder = virtualizer.lengthAtOrder(order);
      const index = indexedPosition.index();
      if (index === 0) {
        if (showsHorizontal(position.type())) {
          for (const cell of elementsAtIndexedPosition(indexedPosition)) {
            cell.classList[operationName]('dragover-top');
          }
        } else {
          for (const cell of elementsAtIndexedPosition(indexedPosition)) {
            cell.classList[operationName]('dragover-left');
          }
        }
      } else {
        const before = new IndexedPosition(position, index - 1);
        if (index === lengthOfOrder) {
          if (showsHorizontal(position.type())) {
            for (const cell of elementsAtIndexedPosition(before)) {
              cell.classList[operationName]('dragover-bottom');
            }
          } else {
            for (const cell of elementsAtIndexedPosition(before)) {
              cell.classList[operationName]('dragover-right');
            }
          }
        } else {
          if (showsHorizontal(position.type())) {
            for (const cell of elementsAtIndexedPosition(before)) {
              cell.classList[operationName]('dragover-thin-bottom');
            }
            for (const cell of elementsAtIndexedPosition(indexedPosition)) {
              cell.classList[operationName]('dragover-thin-top');
            }
          } else {
            for (const cell of elementsAtIndexedPosition(before)) {
              cell.classList[operationName]('dragover-thin-right');
            }
            for (const cell of elementsAtIndexedPosition(indexedPosition)) {
              cell.classList[operationName]('dragover-thin-left');
            }
          }
        }
      }
    }

    const getDragAreaElementsVisitor = {
      visitDimensionDragArea: (position) => {
        return dragIndex.elementsAtPosition(position);
      },
      visitIndexDragArea: (indexedPosition) => {
        return elementsAtIndexedPosition(indexedPosition);
      }
    };

    const highlightDropVisitor = (operationName, indexedPosition) => {
      return {
        visitDimensionDropTarget: (position) => {
          operationOnPosition(operationName, position);
        },
        visitIndexDropTarget: (index) => {
          const targetIndexedPosition =
              new IndexedPosition(indexedPosition.position(), index);
          operationOnIndexedPosition(operationName, targetIndexedPosition);
        },
        visitBinDropTarget: () => {
          binElement.classList[operationName]('dragover-bin');
        },
      };
    };

    const isBinable = (indexedPosition) => {
      const position = indexedPosition.position();
      if (position.type() === 'fixed') { return false; }
      const order = hierarchization.orderOfPosition(position);
      const index = indexedPosition.index();
      return virtualizer.isBinable(order, index);
    }

    const dragNDropStructure = {
      onDragStart: (dragItem) => {
        if (isBinable(dragItem)) {
          binElement.classList.remove('hidden');
        }
      },

      onDragEnd: () => {
          binElement.classList.add('hidden');
      },

      setDraggable: () => {
        for (let cell of dragIndex.allElements()) {
          cell.setAttribute('draggable', 'true');
        }
      },

      determineDragItem: (event) => {
        return dragIndex.valueOfElement(event.target);
      },

      initialDragArea: (indexedPosition) => {
        return new IndexDragArea(indexedPosition);
      },

      setDragging: (dragArea) => {
        for (const cell of dragArea.accept(getDragAreaElementsVisitor)) {
          cell.classList.add('dragging');
        }
      },

      removeDragging: (dragArea) => {
        for (const cell of dragArea.accept(getDragAreaElementsVisitor)) {
          cell.classList.remove('dragging');
        }
      },

      determineTarget: (indexedPosition, event) => {
        return determineDropTarget(indexedPosition.position(), event);
      },

      isDroppable: (indexedPosition, target) => {
        const canDropAtVisitor = {
          visitDimensionDropTarget: (position) => {
            return hierarchization.isMovable(indexedPosition.position(),
                                             position);
          },
          visitIndexDropTarget: (index) => {
            const position = indexedPosition.position();
            const order = hierarchization.orderOfPosition(position);
            return virtualizer.isMovable(order, indexedPosition.index(),
                                                index);
          },
          visitBinDropTarget: () => {
            return isBinable(indexedPosition);
          }
        };
        return target.accept(canDropAtVisitor);
      },

      performDrop: (indexedPosition, target) => {
        const dropVisitor = {
          visitDimensionDropTarget: (position) => {
            const newHierarchization = hierarchization.move(
                                        indexedPosition.position(),
                                        position,
                                        indexedPosition.index());
            return  arrangement.updateHierarchization( newHierarchization);
          },
          visitIndexDropTarget: (index) => {
            const position = indexedPosition.position();
            const order = hierarchization.orderOfPosition(position);
            const newVirtualizer = virtualizer.move(order,
                                        indexedPosition.index(), index);
            return arrangement.updateVirtualizer( newVirtualizer);
          },
          visitBinDropTarget: () => {
            const position = indexedPosition.position();
            const order = hierarchization.orderOfPosition(position);
            const index = indexedPosition.index();
            const newVirtualizer = virtualizer.bin(order, index);
            return arrangement.updateVirtualizer(newVirtualizer);
          }
        };
        const newArrangement = target.accept(dropVisitor);
        const newBigTable = bigTable.updateArrangement(newArrangement);
        div.replaceWith(newBigTable.render());
      },

      dragAreaOfDrop: (indexedPosition, target) => {
        const determineDragAreaOfDropVisitor = {
          visitDimensionDropTarget: (position) => {
            return new DimensionDragArea(indexedPosition.position());
          },
          visitIndexDropTarget: (index) => {
            return new IndexDragArea(indexedPosition);
          },
          visitBinDropTarget: () => {
            return new IndexDragArea(indexedPosition);
          }
        };
        return target.accept(determineDragAreaOfDropVisitor);
      },

      highlight: (indexedPosition, target) => {
        target.accept(highlightDropVisitor('add', indexedPosition));
      },

      removeHighlight: (indexedPosition, target) => {
        target.accept(highlightDropVisitor('remove', indexedPosition));
      }
    }

    attach(dragNDropStructure, div);
  }
}
