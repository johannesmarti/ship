import { Position, Hierarchization } from './hierarchization.mjs';
import { Virtualizer } from './virtualSchema.mjs';

export class IndexedPosition {
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

  toString() {
    return `${this.position()} with index ${this.index()}`;
  }
}

export class Arrangement {
  // could take the base schema here and construct the virtual schema
  // myself
  constructor(hierarchization, virtualizer) {
    this._hierarchization = hierarchization;
    this._virtualizer = virtualizer;
  }

  hierarchization() { return this._hierarchization; }
  virtualizer() { return this._virtualizer; }

  static fromPlainJSON(json) {
    const hierarchizationJSON = json.hierarchization;
    if (hierarchizationJSON === undefined) {
      console.log("ERROR: json object for arrangement order is missing 'hierarchization'");
      return null;
    }
    const virtualizerJSON = json.virtualizer;
    if (virtualizerJSON === undefined) {
      console.log("ERROR: json object for arrangement is missing 'virtualizer'");
      return null;
    }
    const virtualizer = Virtualizer.fromPlainJSON(virtualizerJSON);
    if (virtualizer === null) return null
    let hierarchization = Hierarchization.fromPlainJSON(hierarchizationJSON);
    if (hierarchization === null) return null;
    return new Arrangement(hierarchization, virtualizer);
  }

  toPlainJSON() {
    return {
      hierarchization: this.hierarchization().toPlainJSON(),
      virtualizer: this.virtualizer().toPlainJSON(),
    }
  }

  virtualize(baseSchema) {
    const virtualizer = this.virtualizer();
    virtualizer.checkAgainstSchema(baseSchema);
    const virtualSchema = virtualizer.virtualize(baseSchema);
    const hierarchization = this.hierarchization();
    hierarchization.checkInternally();
    hierarchization.checkAgainstSchema(virtualSchema);
    return virtualSchema;
  }

  updateHierarchization(newHierarchization) {
    return new Arrangement(newHierarchization, this.virtualizer());
  }

  updateVirtualizer(newVirtualizer) {
    return new Arrangement(this.hierarchization(), newVirtualizer);
  }
}
