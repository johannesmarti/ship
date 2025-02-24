export class EqualitySet {
  constructor(array) {
    this._array = array;
  }

  static empty() {
    return new EqualitySet([]);
  }

  contains(element) {
    const ix = this._array.findIndex(e => e.equals(element));
    return ix !== -1;
  }

  elements() {
    return this._array[Symbol.iterator];
  }

  add(element) {
    console.assert(!this.contains(element), `elemement ${element} is
already in the the set '${this._array}'`);
    this._array.push(element);
  }

  toString() {
    return this._array.toString()
  }
}
