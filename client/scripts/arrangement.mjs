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

  static fromJSON(baseSchema, json) {
    const hierarchizationJSON = json.hierarchization;
    if (hierarchizationJSON === undefined) {
      console.log("ERROR: json object for arrangement order is missing 'hierarchization'");
      return null;
    }
    const virtualizerJSON = json.virtualizer;
    if (indexName === undefined) {
      console.log("ERROR: json object for arrangement is missing 'virtualizer'");
      return null;
    }
    const returnValue = Virtualizer.fromJSON(baseSchema, virtualizerJSON);
    if (returnValue === null) return null
    const virtualizer = returnValue.virtualizer;
    let hierarchization = Hierarchization.fromPlainJSON(hierarchizationJSON);
    if (hierarchization === null) return null;
    hierarchization = hierarchization.map(returnValue.orderMap,
                                          returnValue.dependentIndexMap);
    for (let order of returnValue.leftOverOrders) {
      hierarchization = hierarchization.insertAtDefault(order);
    }
    return new Arrangement(hierarchization, virtualizer);
  }

  toJSON(schema) {
    return {
      hierarchization: this.hierarchization().toJSON(),
      virtualizer: this.virtualizer().toJSON(schema),
    }
  }

  updateHierarchization(newHierarchization) {
    return new Arrangement(newHierarchization, this.virtualizer());
  }

  updateVirtualizer(newVirtualizer) {
    return new Arrangement(this.hierarchization(), newVirtualizer);
  }
}
