import { Position, Hierarchization } from './hierarchization.mjs';
import { Virtualizer } from './virtualSchema.mjs';

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

  updateHierarchization(newHierarchization) {
    return new Arrangement(newHierarchization, this.virtualizer());
  }

  updateVirtualizer(newVirtualizer) {
    return new Arrangement(this.hierarchization(), newVirtualizer);
  }
}
