export function isBinable(virtualizer, hierarchization, indexedPosition) {
  const position = indexedPosition.position();
  if (position.type() === 'fixed') { return false; }
  const index = indexedPosition.index();
  const order = hierarchization.orderOfPosition(position);
  return virtualizer.isBinable(order, index);
}

export function bin(virtualizer, hierarchization, indexedPosition) {
  console.assert(isBinable(virtualizer, hierarchization, indexedPosition),
    `trying to bin indexed position ${indexedPosition}, but operation is not possible`);
  const position = indexedPosition.position();
  const order = hierarchization.orderOfPosition(position);
  const index = indexedPosition.index();
  return virtualizer.bin(order, index);
}

export class BinItem {
  constructor(order, baseIndex) {
    this._order = order;
    this._baseIndex = baseIndex;
  }

  static row(offset, baseIndex) {
    return new IndexedPosition(Position.row(offset), baseIndex);
  }

  static column(offset, baseIndex) {
    return new IndexedPosition(Position.column(offset), baseIndex);
  }

  order() { return this._order; }
  baseIndex() { return this._baseIndex; }

  equals(otherIndexedPosition) {
    return this.baseIndex() == otherIndexedPosition.baseIndex() &&
           this.order().equals(otherIndexedPosition.order());
  }

  toString() {
    return `bin item with index ${this.baseIndex()} at order ${this.order()}`;
  }
}

// returns an array of arrays. For every dimension that has restorable
// items there is an array of the binItems
export function binItems(virtualizer, baseSchema) {
  let result = [];
  for (let order of baseSchema.orders()) {
    const descriptor = virtualizer.descriptorAtOrder(order);
    if (descriptor.type !== `remapper`) continue;
    const remapper = descriptor.remapper;
    const dimension = baseSchema.dimensionAtOrder(order);
    const binItemsOfOrder = [];
    for (let index of dimension.indices()) {
      if (remapper.includes(index)) {
        binItemsOfOrder.push(new BinItem(order, index));
      }
    }
    if (binItemsOfOrder.length === 0) continue;
    result.push(binItemsOfOrder);
  }
  return result;
}

export function restore(virtualizer, binItem) {
  return virtualizer.unbin(binItem.order(), binItem.baseIndex(), 0);
}
