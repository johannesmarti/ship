// It might be worth to make this recompute layer fatter so that
// multiple recomputes can happen at the same time! In the current
// approach we get a long chain of calls to lookup when we stack more
// than one recompute.
export class RecomputeLayer {
  constructor(baseData, orderOfRecompute, indexName, recomputer) {
    this._baseData = baseData;
    this._orderOfRecompute = orderOfRecompute;
    const baseSchema = baseData.schema();
    const baseDimension = baseSchema.dimensionAtOrder(orderOfRecompute);
    this._cutoff = baseDimension.numIndices()
    const newDimension = baseDimension.extend(indexName);
    this._schema = baseSchema.updateAtOrder(orderOfRecompute, newDimension);
    this._recomputer = recomputer;
  }

  schema() {
    return this._schema;
  }

  lookup(address) {
    const order = this._orderOfRecompute;
    const cutoff = this._cutoff;
    console.assert(address[order] <= cutoff,
      `absolute address ${address} is out of range in order ${order} with value ${address[order]}`);
    if (address[order] < cutoff) {
      return this._baseData.lookup(address);
    }
    const lookup = (index) => {
      const newAddress = Array.from(address);
      newAddress[order] = index;
      return this._baseData.lookup(newAddress);
    }
    return this._recomputer(lookup);
  }
}
