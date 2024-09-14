import { Schema } from './schema.mjs'

function toAbsoluteIndex(schema, absoluteAddress) {
  console.assert(absoluteAddress.length === schema.numDimensions(),
    `absolute address is not of the right length`);
  let multiplier = 1;
  let absoluteIndex = 0;
  for (let o = schema.numDimensions() - 1; o >= 0; o--) {
    const dimension = schema.dimensionAtOrder(o);
    console.assert(
      dimension.isIndex(absoluteAddress[o]),
      `in order ${o}$ the index in the absolute address ${absoluteAddress} is out of range for the dimension ${dimension.name()}`
    );
    absoluteIndex += absoluteAddress[o] * multiplier;
    multiplier *= dimension.numIndices();
  }
  return absoluteIndex;
}

export class PhysicalData {
  constructor(rawData, schema) {
    this._rawData = rawData;
    this._schema = schema;
  }

  static fromJSON(json) {
    const schema = Schema.fromJSON(json.schema);
    const rawData = json.raw_data;
    return new PhysicalData(rawData, schema);
  }

  schema() {
    return this._schema;
  }

  lookup(absoluteAddress) {
    return this._rawData[toAbsoluteIndex(this._schema, absoluteAddress)];
  }
}

