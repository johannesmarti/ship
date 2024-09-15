export class Position {
  constructor(type, offset) {
    console.assert(type === 'fixed' || type === 'columnHierarchy'
                    || type === 'rowHierarchy',
        `'${type}' is not a supported position type`);
    this._type = type;
    this._offset = offset;
  }

  static fixed(offset) {
    return new Position('fixed', offset);
  }

  static column(offset) {
    return new Position('columnHierarchy', offset);
  }

  static row(offset) {
    return new Position('rowHierarchy', offset);
  }

  type() { return this._type; }
  offset() { return this._offset; }

  toString() {
    return `${this.type()}[${this.offset()}]`;
  }
}

function createPointedOrder(order, fixedIndex) {
  console.assert(schema.isOrder(order), `${order} is not an order in schema`);
  console.assert(schema.dimensionAtOrder(order).isIndex(fixedIndex),
        `${index} is not an index in order ${order}`);
  return {
    "order": order,
    "fixedIndex": fixedIndex
  }
}

function checkPointedOrder(schema, pointedOrder) {
  const order = pointedOrder["order"];
  const fixedIndex = pointedOrder["fixedIndex"];
  console.assert(schema.isOrder(order), `${order} is not an order in schema`);
  console.assert(schema.dimensionAtOrder(order).isIndex(fixedIndex),
        `${index} is not an index in order ${order}`);
}

export class Arrangement {
  constructor(fixed, rowHierarchy, columnHierarchy) {
    this._fixed = fixed;
    this._rowHierarchy = rowHierarchy;
    this._columnHierarchy = columnHierarchy;
  }

  static create(fixed, rowHierarchy, columnHierarchy) {
    const newArrangement = new Arrangement(fixed, rowHierarchy,
                                                  columnHierarchy);
    newArrangement.checkInternally();
    return newArrangement;
  }

  checkInternally() {
    const pos = this._fixed;
    const fSet = new Set(pos.map(po => po["orders"]))
    const [rowHierarchy, columnHierarchy] = this.hierarchies()
    const rSet = new Set(rowHierarchy);
    const cSet = new Set(columnHierarchy);
    console.assert(rowHierarchy.length > 0 || pos.length > 0,
      "row hierarchy is empty and there are no fixed values");
    console.assert(columnHierarchy.length > 0 || pos.length > 0,
      "column hierarchy is empty and there are no fixed values");
    console.assert(fSet.size === pos.length,
      "ponted orders contain duplicates");
    console.assert(rSet.size === rowHierarchy.length,
      "row hierarchy contains duplicates");
    console.assert(cSet.size === columnHierarchy.length,
      "column hierarchy contains duplicates");
    console.assert(rowHierarchy.every(item => !cSet.has(item)),
      "row and column hierarchies are not disjoint");
    console.assert(rowHierarchy.every(item => !fSet.has(item)),
      "row hierarchy and pointed orders are not disjoint");
    console.assert(columnHierarchy.every(item => !fSet.has(item)),
      "column hierarchy and pointed orders are not disjoint");
  }

  checkAgainstSchema(schema) {
    const pos = this._fixed;
    const fSet = new Set(pos.map(po => po["orders"]))
    const [rowHierarchy, columnHierarchy] = this.hierarchies()
    const rSet = new Set(rowHierarchy);
    const cSet = new Set(columnHierarchy);
    for (let o = 0; o < schema.numDimensions(); o++) {
      console.assert(fSet.has(o) || rSet.has(o) || cSet.has(o),
        "some dimension from the schema is not in either row nor column hierarchy");
    }
    console.assert(this.numOrders() === schema.numDimensions(),
      "arrangement contains orders that are not in the schema");

    for (let pointedOrder of this._fixed) {
      checkPointedOrder(schema, pointedOrder);
    }
  }

  hierarchies() {
    return [this._rowHierarchy, this._columnHierarchy];
  }

  numOrders() {
    return this._fixed.length
         + this._rowHierarchy.length
         + this._columnHierarchy.length;
  }

  arrayOfType(type) {
    switch (type) {
      case 'fixed':
        return this._fixed;
      case 'rowHierarchy':
        return this._rowHierarchy;
      case 'columnHierarchy':
        return this._columnHierarchy;
    }
    console.assert(false, `position type should be 'fixed', 'rowHierarchy' or 'columnHierarchy', but is '${type}'`);
  }

  setArrayOfType(type, array) {
    switch (type) {
      case 'fixed':
        return new Arrangement(array, this._rowHierarchy, this._columnHierarchy);
      case 'rowHierarchy':
        return new Arrangement(this._fixed, array, this._columnHierarchy);
      case 'columnHierarchy':
        return new Arrangement(this._fixed, this._rowHierarchy, array);
    }
    console.assert(false, `position type should be 'fixed', 'rowHierarchy' or 'columnHierarchy', but is '${type}'`);
  }

  isPosition(position) {
    const offset = position.offset();
    if (offset < 0) return false;
    return offset < this.arrayOfType(position.type()).length;
  }

  isDropPosition(position) {
    const offset = position.offset();
    if (offset < 0) return false;
    return offset <= this.arrayOfType(position.type()).length;
  }

  isMovable(fromPosition, toPosition) {
    console.assert(this.isPosition(fromPosition),
      `position ${fromPosition} is not a position in arrangement`);
    console.assert(this.isDropPosition(toPosition),
      `position ${toPosition} is not a drop position in arrangement`);

    if (toPosition.type() === fromPosition.type() &&
        (toPosition.offset() === fromPosition.offset() ||
         toPosition.offset() === fromPosition.offset() + 1)) {
        return false;
    }
    if (this.arrayOfType(fromPosition.type()).length <= 1) {
      switch (fromPosition.type()) {
        case 'fixed':
          switch (toPosition.type()) {
            case 'fixed':
              console.assert(false, "the impossible happened");
              break;
            case 'rowHierarchy':
              if (this._columnHierarchy.length <= 0) return false;
              break;
            case 'columnHierarchy':
              if (this._rowHierarchy.length <= 0) return false;
              break;
          }
          break;
        case 'rowHierarchy':
          switch (toPosition.type()) {
            case 'fixed':
              break;
            case 'rowHierarchy':
              console.assert(false, "the impossible happened");
              break;
            case 'columnHierarchy':
              if (this._fixed.length <= 0) return false;
              break;
          }
          break;
        case 'columnHierarchy':
          switch (toPosition.type()) {
            case 'fixed':
              break;
            case 'rowHierarchy':
              if (this._fixed.length <= 0) return false;
              break;
            case 'columnHierarchy':
              console.assert(false, "the impossible happened");
              break;
          }
          break;
      }
    }
    return true;
  }

  move(fromPosition, toPosition, fixedIndex) {
    this.checkInternally();
    console.assert(this.isMovable(fromPosition, toPosition),
      `trying to move ${fromPosition} to ${toPosition}, but operation is not possible`);

    const fromType = fromPosition.type();
    const fromOffset = fromPosition.offset();
    const toType = toPosition.type();
    const toOffset = toPosition.offset();
    const fromArray = this.arrayOfType(fromType);
    if (fromType === toType) {
      const array = fromArray;
      const mover = array[fromOffset];
      let newArray;
      if (fromOffset < toOffset) {
        newArray = [...array.slice(0, fromOffset),
                    ...array.slice(fromOffset + 1, toOffset), mover,
                    ...array.slice(toOffset)];
      } else {
        newArray = [...array.slice(0, toOffset), mover,
                    ...array.slice(toOffset, fromOffset),
                    ...array.slice(fromOffset + 1)];
      }
      return this.setArrayOfType(fromType, newArray);
    } else {
      const fromElement = fromArray[fromOffset];
      const order = fromType !== 'fixed' ? fromElement : fromElement['order'];
      const newElement = toType !== 'fixed' ? order
                            : { 'order': order, 'fixedIndex': fixedIndex };
      const toArray = this.arrayOfType(toType);
      const newFromArray = [...fromArray.slice(0, fromOffset),
                            ...fromArray.slice(fromOffset + 1)];
      const newToArray = [...toArray.slice(0, toOffset), newElement,
                          ...toArray.slice(toOffset)];
      return this.setArrayOfType(fromType, newFromArray)
                 .setArrayOfType(toType, newToArray);
    }
  }

  absoluteAddress(rowAddress, columnAddress) {
    const [rowHierarchy, columnHierarchy] = this.hierarchies();
    console.assert(rowAddress.length === rowHierarchy.length,
      "row address length does not match the length of the row hierarchy");
    console.assert(columnAddress.length === columnHierarchy.length,
      "column address length does not match the length of the column hierarchy");

    const address = Array(this.numOrders());
    for (const pointedOrder of this._fixed) {
      address[pointedOrder["order"]] = pointedOrder["fixedIndex"];
    }
    for (const [offset, index] of rowAddress.entries()) {
      address[rowHierarchy[offset]] = index;
    }
    for (const [offset, index] of columnAddress.entries()) {
      address[columnHierarchy[offset]] = index;
    }
    return address;
  }
}

