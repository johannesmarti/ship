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
  constructor(pointedOrders, rowHierarchy, columnHierarchy) {
    this._pointedOrders = pointedOrders;
    this._rowHierarchy = rowHierarchy;
    this._columnHierarchy = columnHierarchy;
    checkInternally();
  }

  checkInternally() {
    const pos = this._pointedOrders;
    const fSet = new Set(pos.map(po => po["orders"]))
    const [rowHierarchy, columnHierarchy] = this.hierarchies()
    const rSet = new Set(rowHierarchy);
    const cSet = new Set(columnHierarchy);
    console.assert(rowHierarchy.length > 0 || pos.length > 0,
      "row hierarchy is empty and there are no pointed orders");
    console.assert(columnHierarchy.length > 0 || pos.length > 0,
      "column hierarchy is empty and there are no pointed orders");
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

  // TODO: This check needs to be adapted
  checkHierarchiesAgainstSchema(schema) {
    for (let o = 0; o < schema.numDimensions(); o++) {
      console.assert(rSet.has(o) || cSet.has(o),
        "some dimension from the schema is not in either row nor column hierarchy");
    }
    console.assert(rSet.size + cSet.size === schema.numDimensions(),
      "row or column hierarchy contain dimensions that are not in the schema");
  }

  hierarchies() {
    return [this._rowHierarchy, this._columnHierarchy];
  }

  numOrders() {
    return this._pointedOrders.length
         + this._rowHierarchy.length
         + this._columnHierarchy.length;
  }

  absoluteAddress(rowAddress, columnAddress) {
    const [rowHierarchy, columnHierarchy] = this.hierarchies();
    console.assert(rowAddress.length === rowHierarchy.length,
      "row address length does not match the length of the row hierarchy");
    console.assert(columnAddress.length === columnHierarchy.length,
      "column address length does not match the length of the column hierarchy");

    const address = Array(this.numOrders());
    for (const pointedOrder of this._pointedOrders) {
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

