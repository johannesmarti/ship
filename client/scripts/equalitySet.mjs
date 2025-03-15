import { AATree } from './aatree.mjs';

class ArrayEqualitySet {
  constructor(array) {
    this._array = array;
  }

  static empty(compare) {
    return new ArrayEqualitySet([]);
  }

  contains(element) {
    const ix = this._array.findIndex(e => e.equals(element));
    return ix !== -1;
  }

  elements() {
    return this._array.values();
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

export class TreeEqualitySet {
  constructor(compare) {
    this._aatree = AATree(compare);
  }

  static empty(compare) {
    return new TreeEqualitySet(compare);
  }

  contains(element) {
    const ix = this._array.findIndex(e => e.equals(element));
    return ix !== -1;
  }

  elements() {
    return this._array.values();
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

//const EqualitySet = ArrayEqualitySet;
const EqualitySet = TreeEqualitySet;

export {EqualitySet};
