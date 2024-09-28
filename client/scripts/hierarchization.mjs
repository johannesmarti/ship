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

  equals(other) {
    return this.offset() === other.offset() && this.type() === other.type();
  }

  type() { return this._type; }
  offset() { return this._offset; }

  toString() {
    return `${this.type()}[${this.offset()}]`;
  }
}

class PointedOrder {
  constructor(order, fixedIndex) {
    this._order = order;
    this._fixedIndex = fixedIndex;
  }

  checkAgainstSchema(schema) {
    const order = this._order;
    const fixedIndex = this._fixedIndex
    console.assert(schema.isOrder(order), `${order} is not an order in schema`);
    console.assert(schema.dimensionAtOrder(order).isIndex(fixedIndex),
          `${fixedIndex} is not an index in order ${order}`);
  }

  order() { return this._order; }
  fixedIndex() { return this._fixedIndex; }

  // returns null if the json object is not of the right format or there
  // is no there is no such dimension in schema
  static fromJSON(schema, json) {
    const dimensionName = json.dimension;
    const indexName = json.fixedIndex;
    if (dimensionName === undefined || indexName === undefined) {
      console.log('ERROR: json object for pointed order is not of the right format');
      return null;
    }
    const order = schema.orderOfDimensionName(dimensionName);
    if (order === -1) {
      console.log(`WARNING: '${dimensionName}' is not the name of any dimension in schema`);
      return null;
    }
    let index = schema.dimensionAtOrder(order).indexOfName(indexName);
    if (index === -1) {
      console.log(`WARNING: '${indexName}' is not the name of any index in dimension ${dimensionName}`);
      index = 0;
    }
    return new PointedOrder(order, index);
  }

  toJSON(schema) {
    const dimension = schema.dimensionAtOrder(this._order);
    return {
      dimension: dimension.name(),
      fixedIndex: dimension.nameOfIndex(this._fixedIndex)
    };
  }

  // returns null if the json object is not of the right format
  static fromPlainJSON(json) {
    const order = json.order;
    const fixedIndex = json.fixedIndex;
    if (order === undefined) {
      console.log("ERROR: json object for pointed order is not of the right format, needs a field 'order'");
      return null;
    }
    if (fixedIndex === undefined) {
      console.log("ERROR: json object for pointed order is not of the right format, needs a field 'index'");
      return null;
    }
    if (!Number.isInteger(order)) {
      console.log(`ERROR: json object for pointed order needs a number
at 'order', but got ${order}`);
      return null;
    }
    if (!Number.isInteger(fixedIndex)) {
      console.log(`ERROR: json object for pointed order needs a number
at 'fixedIndex', but got ${fixedIndex}`);
      return null;
    }
    return new PointedOrder(order, fixedIndex);
  }

  toPlainJSON() {
    return {
      order: this.order(),
      fixedIndex: this.fixedIndex()
    };
  }
}

export class Hierarchization {
  constructor(fixed, rowHierarchy, columnHierarchy) {
    this._fixed = fixed;
    this._rowHierarchy = rowHierarchy;
    this._columnHierarchy = columnHierarchy;
  }

  static create(fixed, rowHierarchy, columnHierarchy) {
    const newHierarchization = new Hierarchization(fixed, rowHierarchy,
                                                  columnHierarchy);
    newHierarchization.checkInternally();
    return newHierarchization;
  }

  checkInternally() {
    const pos = this._fixed;
    const fSet = new Set(pos.map(po => po.order()))
    const [rowHierarchy, columnHierarchy] = this.hierarchies()
    const rSet = new Set(rowHierarchy);
    const cSet = new Set(columnHierarchy);
    console.assert(rowHierarchy.length > 0 || pos.length > 0,
      "row hierarchy is empty and there are no fixed values");
    console.assert(columnHierarchy.length > 0 || pos.length > 0,
      "column hierarchy is empty and there are no fixed values");
    console.assert(fSet.size === pos.length,
      "pointed orders contain duplicates");
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
    const fSet = new Set(pos.map(po => po.order()))
    const [rowHierarchy, columnHierarchy] = this.hierarchies()
    const rSet = new Set(rowHierarchy);
    const cSet = new Set(columnHierarchy);
    for (let o = 0; o < schema.numDimensions(); o++) {
      console.assert(fSet.has(o) || rSet.has(o) || cSet.has(o),
        `dimension ${o} from the schema is not in either row nor column hierarchy, nor is it fixed`);
    }
    console.assert(this.numOrders() === schema.numDimensions(),
      "hierarchization contains orders that are not in the schema");

    for (let pointedOrder of this._fixed) {
      pointedOrder.checkAgainstSchema(schema);
    }
  }

  fixed() { return this._fixed; }
  hierarchies() { return [this._rowHierarchy, this._columnHierarchy]; }

  // returns null if json is not of the right structure
  static fromJSON(schema, json) {
    function hierarchyFromJSON(list) {
      if (list === undefined) {
        console.log(`ERROR: JSON object for hierarchization is not of the right format`);
        return 'formatError';
      }
      const result = [];
      for (const name of list) {
        const order = schema.orderOfDimensionName(name);
        if (order === -1) {
          console.log(`WARNING: '${name}' is not the name of any dimension in schema`);
        } else {
          result.push(order);
        }
      }
      return result;
    }
    const rowHierarchy = hierarchyFromJSON(json['rowHierarchy']);
    if (rowHierarchy === 'formatError') { return null; }
    const columnHierarchy = hierarchyFromJSON(json['columnHierarchy']);
    if (columnHierarchy === 'formatError') { return null; }

    const fixed = [];
    const fixedJSON = json['fixed'];
    if (fixedJSON === undefined) {
      console.log(`ERROR: JSON object for hierarchization is no of the righformat`);
      return null;
    }
    for (const jsonElement of fixedJSON) {
      const po = PointedOrder.fromJSON(schema, jsonElement);
      if (po !== null) {
        fixed.push(po);
      }
    }

    // since orders are just numbers in a range 0 ... n we could also
    // just use an array to store the accounted orders. This would be
    // much more efficient than a set, but maybe less clean?
    const fixedOrders = fixed.map( po => po.order() );
    const coveredDimensions = new Set([...fixedOrders,
                                       ...rowHierarchy, ...columnHierarchy]);
    for (const order of schema.orders()) {
      if (!coveredDimensions.has(order)) {
        const name = schema.dimensionAtOrder(order).name();
        console.log(`WARNING: dimension ${name} is not accounted for in JSON hierarchization`);
        fixed.push(new PointedOrder(order, 0));
      }
    }

    const hierarchization = Hierarchization.create(fixed, rowHierarchy, columnHierarchy);
    hierarchization.checkAgainstSchema(schema);
    return hierarchization;
  }

  toJSON(schema) {
    return {
      'fixed': this._fixed.map(po => po.toJSON(schema)),
      'rowHierarchy': this._rowHierarchy.map( order =>
            schema.dimensionAtOrder(order).name() ),
      'columnHierarchy': this._columnHierarchy.map( order =>
            schema.dimensionAtOrder(order).name() )
    };
  }

  static fromPlainJSON(json) {
    function hierarchyFromJSON(list) {
      if (list === undefined) {
        console.log(`ERROR: JSON object for hierarchization is not of the right format`);
        return null;
      }
      for (const order of list) {
        if (!Number.isInteger(order)) { return null; }
      }
      return list;
    }
    const rowHierarchy = hierarchyFromJSON(json.rowHierarchy);
    if (rowHierarchy === null) { return null; }
    const columnHierarchy = hierarchyFromJSON(json.columnHierarchy);
    if (columnHierarchy === null) { return null; }

    const fixed = [];
    const fixedJSON = json.fixed;
    if (fixedJSON === undefined) {
      console.log(`ERROR: JSON object for hierarchization is no of the righformat`);
      return null;
    }
    for (const jsonElement of fixedJSON) {
      const po = PointedOrder.fromPlainJSON(jsonElement);
      if (po === null) { return null; }
      fixed.push(po);
    }

    return Hierarchization.create(fixed, rowHierarchy, columnHierarchy);
  }

  toPlainJSON() {
    const [rowHierarchy, columnHierarchy] = this.hierarchies();
    return {
      fixed: this.fixed().map(po => po.toPlainJSON()),
      rowHierarchy: rowHierarchy,
      columnHierarchy: columnHierarchy
    };
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
        return new Hierarchization(array, this._rowHierarchy, this._columnHierarchy);
      case 'rowHierarchy':
        return new Hierarchization(this._fixed, array, this._columnHierarchy);
      case 'columnHierarchy':
        return new Hierarchization(this._fixed, this._rowHierarchy, array);
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
      `position ${fromPosition} is not a position in hierarchization`);
    console.assert(this.isDropPosition(toPosition),
      `position ${toPosition} is not a drop position in hierarchization`);

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
      const order = fromType !== 'fixed' ? fromElement : fromElement.order();
      const newElement = toType !== 'fixed' ? order
                            : new PointedOrder(order, fixedIndex);
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
      address[pointedOrder.order()] = pointedOrder.fixedIndex();
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

