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

  updateHierarchization(newHierarchization) {
    return new Arrangement(newHierarchization, this.virtualizer());
  }

  updateVirtualizer(newVirtualizer) {
    return new Arrangement(this.hierarchization(), newVirtualizer);
  }

/*
  checkAgainstSchema(schema) {
    this.hierarchization().checkAgainstSchema(schema);
    this.virtualizer().checkAgainstSchema(schema);
  }
*/
}
