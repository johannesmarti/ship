import { Schema } from './schema.mjs';
import { Position, Arrangement } from './arrangement.mjs';

export function h(tagName, ...args) {
  const el = document.createElement(tagName);
  el.append(...args);
  return el;
}

function createButton(text, onClickFunction) {
  let button = document.createElement("button");
  button.textContent = text;
  button.onclick = onClickFunction;
  return button;
}

class IdentityDimensionTransformer {
  constructor(baseDimension) {
    this._baseDimension = baseDimension;
  }

  numIndices() {
    return this._baseDimension.numIndices();
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._baseDimension.name();
  }

  nameOfIndex(index) {
    return this._baseDimension.nameOfIndex(index);
  }

  transform(index) {
    return index;
  }
}

class FixedValueDimensionTransformer {
  constructor(baseDimension, fixedIndex) {
    this._baseDimension = baseDimension;
    this._fixedIndex = fixedIndex;
  }

  nameOfFixedIndex() {
    return this._baseDimension.nameOfIndex(this._fixedIndex);
  }

  numIndices() {
    return 1;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._baseDimension.name() + `[${this.nameOfFixedIndex()}]`;
  }

  nameOfIndex(index) {
    console.assert(index === 0,
      `${index} is not a index in the fixed dimension ${this.name()} because it is not equal to 0`);
    return this.nameOfFixedIndex(); 
  }

  transform(index) {
    return this._fixedIndex;
  }
}

class RemappingDimensionTransformer {
  constructor(baseDimension, remapper, name) {
    this._baseDimension = baseDimension;
    this._remapper = remapper;
    this._name = name;
  }

  numIndices() {
    return this._remapper.length;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._name;
  }

  nameOfIndex(index) {
    return this._baseDimension.nameOfIndex(this.transform(index)); 
  }

  transform(index) {
    console.assert(0 <= index && index < this.numIndices(),
      `${index} is not a index in the remapping dimension ${this.name()}`);

    return this._remapper[index];
  }
}

function exponentialRemapper(baseDimension, center) {
  console.assert(0 <= center && center < baseDimension.numIndices(),
    `center point ${center} is not a index in the base dimension ${baseDimension.name()}`);
  // This could be computed more efficiently. I don't care.
  const remapper = [center];
  {
    let dist = 1;
    if (center !== 0) {
      while (true) {
        if (center - dist <= 0) {
          remapper.unshift(0);
          break;
        }
        remapper.unshift(center - dist);
        dist *= 2;
      }
    }
  }
  {
    let dist = 1;
    const last = baseDimension.numIndices() - 1;
    if (center !== last) {
      while (true) {
        if (center + dist >= last) {
          remapper.push(last);
          break;
        }
        remapper.push(center + dist);
        dist *= 2;
      }
    }
  }

  const name = `exponential remapper on ${baseDimension.name()} around
${baseDimension.nameOfIndex(center)}`;
  return new RemappingDimensionTransformer(baseDimension, remapper, name);
}

class TransformedDataView {
  constructor(physicalView, transformationSchema) {
    this._physicalView = physicalView;
    this._transformationSchema = transformationSchema;
  }

  schema() {
    return this._transformationSchema;
  }
  
  lookup(absoluteAddress) {
    const schema = this.schema();
    const physicalAddress = new Array(absoluteAddress.length);
    for (let o of schema.orders()) {
      physicalAddress[o] = schema.dimensionAtOrder(o).transform(absoluteAddress[o]);
    }
    return this._physicalView.lookup(physicalAddress);
  }
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

function indexInDimensionFromJSON(dimension, json) {
  const defaultValue = 0;
  return {
    "first": 0,
    "mid": dimension.numIndices() / 2,
    "last": dimension.numIndices() - 1
  }[json] || (Number.isInteger(json) ? json : defaultValue);
}

export class Virtualizer {
  constructor(configuration) {
    this._configuration = configuration;
  }

  configuration() {
    return this._configuration;
  }

  virtualize(schema) {
    const array = schema._dimensions.map((_, o) => {
      const dimension = schema.dimensionAtOrder(o);
      const descriptor = this._configuration[o] || {"type": "id"};

      const id = () => new IdentityDimensionTransformer(dimension);
      const onFixed = () => {
            const fixedValue = indexInDimensionFromJSON(dimension, descriptor["value"]);
            return new FixedValueDimensionTransformer(dimension, fixedValue);
      };
      const mapper = {
        "id": id,
        "fixed": onFixed,
        "fixed_id": onFixed,
        "fixed_exponential": onFixed,
        "exponential": () => {
            const center = indexInDimensionFromJSON(dimension, descriptor["center"]);
            return exponentialRemapper(dimension, center);
          }
      }[descriptor["type"]] || id;
      return mapper();
    });
    return new Schema(array);
  }

  update(order, baseIndex, baseDimension) {
    const configuration = this.configuration();
    const description = configuration[order] || {"type": "id"};
    const currentType = description["type"] || "id";
    const computeNewDescription = {
      "id": () => { return {"type": "fixed_id", "value": baseIndex}; },
      "fixed": () => { return {"type": "id"}; },
      "fixed_id": () => { return {"type": "id"}; },
      "fixed_exponential": () => {
          return {"type": "exponential",
                  "center": description["value"]};
        },
      "exponential": () => {
          const center = indexInDimensionFromJSON(baseDimension,
            description["center"]);
          if (baseIndex === center) {
            return {"type": "fixed_exponential",
                    "value": description["center"]};
          } else {
            return {"type": "exponential",
                    // TODO: Here we could make an effort to
                    // reconstruct the JSON descriptors "first",
                    // "mid" and "last".
                    "center": baseIndex};
          }
        }
    }[currentType];
    const newDescription = computeNewDescription()
    const newConfiguration = { ...configuration, [order]: newDescription};
    const newVirtualizer = new Virtualizer(newConfiguration);
    return newVirtualizer;
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
  constructor(dataView) {
    this._dataView = dataView;
  }

  addListeners(dragIndex, unitIndex, div, arrangement, virtualizer) {
    for (let cell of dragIndex.allElements()) {
      cell.setAttribute('draggable', 'true');
    } 
    let dragging = null;
    let highlighted = null;

    function determineDropPosition(event) {
      const target = event.target.closest('th');
      if (target === null) { return null; }
      const overPosition = dragIndex.positionOfElement(target);
      if (overPosition === null) { 
        const unitPosition = unitIndex.positionOfElement(target);
        if (unitPosition === null) return null;
        else return unitPosition;
      }

      const boundingRectangle = target.getBoundingClientRect();
      if (isHorizontal(overPosition.type())) {
        const xOffset = event.clientX - boundingRectangle.left;
        if (xOffset < boundingRectangle.width / 2) {
          return overPosition;
        } else {
          return new Position(overPosition.type(), overPosition.offset() + 1);
        }
      } else {
        const yOffset = event.clientY - boundingRectangle.top;
        if (yOffset < boundingRectangle.height / 2) {
          return overPosition;
        } else {
          return new Position(overPosition.type(), overPosition.offset() + 1);
        }
      }
    }

    function operationOnPositions(operationName, position) {
      if (arrangement.isPosition(position)) {
        if (isHorizontal(position.type())) {
          for (const cell of dragIndex.elementsAtPosition(position)) {
            cell.classList[operationName]('dragover-left');
          }
        } else {
          for (const cell of dragIndex.elementsAtPosition(position)) {
            cell.classList[operationName]('dragover-top');
          }
        }
      } else if (arrangement.isDropPosition(position)) {
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

    function highlight(position) {
      operationOnPositions('add', position);
    }

    // should be abstracted together with the previous
    function removeHighlighting(position) {
      operationOnPositions('remove', position);
    }

    div.addEventListener('dragstart', (event) => {
      const indexedPosition = dragIndex.valueOfElement(event.target);
      dragging = indexedPosition;
      const position = indexedPosition.position();
      for (const cell of dragIndex.elementsAtPosition(position)) {
        cell.classList.add('dragging');
      }
    });

    div.addEventListener('dragover', (event) => {
      console.assert(dragging !== null,
        `there is a dragging element on dragover event`);
      // I do not understand why this preventDefault is needed
      event.preventDefault();
      const target = determineDropPosition(event);
      if (target === null) { return; }
      if (highlighted !== null) {
        if (target.equals(highlighted)) { return; }
        removeHighlighting(highlighted);
        highlighted = null;
      }
      if (arrangement.isMovable(dragging.position(), target)) {
        highlight(target);
        highlighted = target;
      }
    });

    div.addEventListener('drop', (event) => {
      if (highlighted == null) { return; }
      const newArrangement = arrangement.move(dragging.position(), highlighted,
                                              dragging.index());
      div.replaceWith(this.render(newArrangement, virtualizer));
    });

    div.addEventListener('dragend', (event) => {
      console.assert(dragging !== null,
        `there is a dragging element on dragend event`);
      for (const cell of dragIndex.elementsAtPosition(dragging.position())) {
        cell.classList.remove('dragging');
      }
      dragging = null;
      if (highlighted !== null) {
        removeHighlighting(highlighted);
        highlighted = null;
      }
    });
  }

  render(arrangement, virtualizer) {
    const baseSchema = this._dataView.schema();
    // could be done in constructor, need to think how I do this stuff
    // in the interface
    const schema = virtualizer.virtualize(baseSchema);
    arrangement.checkInternally();
    arrangement.checkAgainstSchema(schema);
    const transformedDataView = new TransformedDataView(this._dataView, schema);
    arrangement.checkAgainstSchema(schema);
    const [rowHierarchy, columnHierarchy] = arrangement.hierarchies();

    localStorage.setItem('arrangement', JSON.stringify(arrangement.toJSON(schema)));

    const dragIndex = new PositionIndex(
        (indexedPosition) => indexedPosition.position(),
        arrangement.fixed().length,
        rowHierarchy.length, columnHierarchy.length);

    const unitIndex = new PositionIndex(
        (position) => position,
        arrangement.fixed().length === 0 ? 1 : 0,
        rowHierarchy.length === 0 ? 1 : 0,
        columnHierarchy.length === 0 ? 1 : 0);

    let frow;
    let tbody;
    let div = h("div",
        h("table", h("tbody", frow = h("tr"))),
        h("table", tbody = h("tbody"))
    );

    // draw fixed entries
    if (arrangement.fixed().length === 0) {
      const cell = h("th", "\u2605");
      unitIndex.add(cell, Position.fixed(0));
      frow.append(cell);
    } else {
      for (const [offset, fixedOrder] of arrangement.fixed().entries()) {
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
        const baseDimension = baseSchema.dimensionAtOrder(order);
        const baseIndex = dimension.transform(index);
        const newVirtualizer =
            virtualizer.update(order, baseIndex, baseDimension);
        div.replaceWith(this.render(arrangement, newVirtualizer));
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

    function drawDataPartOfRow(row, rowAddress) {
      const columnIterator = new MutableHierarchicalIterator(schema, columnHierarchy);
      do {
        const address = arrangement.absoluteAddress(rowAddress,
                                                    columnIterator.address());
        const value = transformedDataView.lookup(address);
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
          // TODO: need to understand whether to save virtualized
          // indices or base indices
          dragIndex.add(cell, IndexedPosition.row(k, index));
          row.prepend(cell);
          multiplier *= dimension.numIndices();
        }
        drawDataPartOfRow(row, rowIterator.address());
        tbody.append(row);
      } while (rowIterator.increment());
    }
    this.addListeners(dragIndex, unitIndex, div, arrangement, virtualizer);
    return div;
  }
}
