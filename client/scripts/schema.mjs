class Dimension {
  constructor(name, indexNameList) {
    this._name = name;
    this._indexNameList = indexNameList;
    console.assert(this._indexNameList.length >= 1,
      `Need at least one index in dimension ${this._name}`);
  }

  static fromJSON(spec) {
    return new Dimension(spec.name, spec.indices);
  }

  numIndices() {
    return this._indexNameList.length;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._name;
  }

  nameOfIndex(index) {
    console.assert(this.isIndex(index),
      `${index} is not an index in dimension ${this.name()}`);
    return this._indexNameList[index];
  }

  indexOfName(name) {
    return this._indexNameList.indexOf(name);
  }

  extend(newIndexName) {
    const newIndexNameList = Array.from(this._indexNameList);
    newIndexNameList.push(newIndexName);
    return new Dimension(this._name, newIndexNameList);
  }
}

export class Schema {
  constructor(dimensions) {
    this._dimensions = dimensions;
  }

  static fromJSON(json) {
    return new Schema(json.map((spec) => Dimension.fromJSON(spec)));
  }

  isOrder(number) {
    return 0 <= number && number < this.numDimensions();
  }

  *orders() {
    for (let order = 0; order < this.numDimensions(); order++) {
      yield order;
    }
  }

  numDimensions() {
    return this._dimensions.length;
  }

  dimensionAtOrder(order) {
    console.assert(this.isOrder(order), `${order} is not an order in schema`);
    return this._dimensions[order];
  }

  orderOfDimensionName(dimensionName) {
    return this._dimensions.findIndex((c) => c.name() === dimensionName);
  }

  dimensionOfName(dimensionName) {
    return this.dimensionAtOrder(this.orderOfDimensionName(dimensionName));
  }

  updateAtOrder(order, newDimension) {
    const newDimensions = Array.from(this._dimensions);
    newDimensions[order] = newDimension;
    return new Schema(newDimensions);
  }
}
