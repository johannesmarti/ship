import { Schema } from './schema.mjs';

class IdentityDimensionTransformer {
  constructor(baseDimension) {
    this._baseDimension = baseDimension;
  }

  numIndices() {
    return this._baseDimension.numIndices();
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._baseDimension.name();
  }

  nameOfIndex(index) {
    return this._baseDimension.nameOfIndex(index);
  }

  transform(index) {
    return index;
  }
}

class RemappingDimensionTransformer {
  constructor(baseDimension, remapper, name) {
    for (let baseIndex of remapper) {
      console.assert(baseDimension.isIndex(baseIndex),
        `center point ${baseIndex} is not a index in the base dimension ${baseDimension.name()}`);
    }
    this._baseDimension = baseDimension;
    this._remapper = remapper;
    this._name = name;
  }

  numIndices() {
    return this._remapper.length;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._name;
  }

  nameOfIndex(index) {
    return this._baseDimension.nameOfIndex(this.transform(index)); 
  }

  transform(index) {
    console.assert(0 <= index && index < this.numIndices(),
      `${index} is not a index in the remapping dimension ${this.name()}`);

    return this._remapper[index];
  }
}

function exponentialRemapper(baseDimension, center) {
  console.assert(baseDimension.isIndex(center),
    `center point ${center} is not a index in the base dimension ${baseDimension.name()}`);
  // This could be computed more efficiently. I don't care.
  const remapper = [center];
  {
    let dist = 1;
    if (center !== 0) {
      while (true) {
        if (center - dist <= 0) {
          remapper.unshift(0);
          break;
        }
        remapper.unshift(center - dist);
        dist *= 2;
      }
    }
  }
  {
    let dist = 1;
    const last = baseDimension.numIndices() - 1;
    if (center !== last) {
      while (true) {
        if (center + dist >= last) {
          remapper.push(last);
          break;
        }
        remapper.push(center + dist);
        dist *= 2;
      }
    }
  }

  const name = `exponential remapper on ${baseDimension.name()} around ${baseDimension.nameOfIndex(center)}`;
  return new RemappingDimensionTransformer(baseDimension, remapper, name);
}

function explicitRemapper(baseDimension, remapper) {
  const name = `explicity remapper on ${baseDimension.name()} from ${remapper}`;
  return new RemappingDimensionTransformer(baseDimension, remapper, name);
}

export class TransformedDataView {
  constructor(physicalView, transformationSchema) {
    this._physicalView = physicalView;
    this._transformationSchema = transformationSchema;
  }

  schema() {
    return this._transformationSchema;
  }
  
  lookup(absoluteAddress) {
    const schema = this.schema();
    const physicalAddress = new Array(absoluteAddress.length);
    for (let o of schema.orders()) {
      physicalAddress[o] = schema.dimensionAtOrder(o).transform(absoluteAddress[o]);
    }
    return this._physicalView.lookup(physicalAddress);
  }
}

function indexInDimensionFromJSON(dimension, json) {
  const defaultValue = 0;
  return {
    "first": 0,
    "mid": dimension.numIndices() / 2,
    "last": dimension.numIndices() - 1
  }[json] || (Number.isInteger(json) ? json : defaultValue);
}

function jsonForDimensionFromIndex(dimension, index) {
  if (index === 0) return "first";
  const numIndices = dimension.numIndices();
  if (index === numIndices / 2) return "mid";
  if (index === numIndices - 1) return "last";
  return index;
}

export class Virtualizer {
  constructor(descriptorArray) {
    this._descriptorArray = descriptorArray;
  }

  static fromConfiguration(configuration, length) {
    const descriptorArray = new Array(length);
    for (let order = 0; order < length; order++) {
      descriptorArray[order] = configuration[order] || {type: "id"};
    }
    return new Virtualizer(descriptorArray);
  }

  checkAgainstSchema(schema) {
    const thisLength = this._descriptorArray.length;
    console.assert(thisLength === schema.numDimensions(), 
      `schema has ${schema.numDimensions()} dimensions but virtualizer
is of length ${thisLength}`);
  }

  static fromPlainJSON(json) {
    function isNaturalNumber(value) {
      return typeof value === "number" &&
             Number.isInteger(value) &&
             value >= 0;
    }
    if (!Array.isArray(json)) {
      console.log("ERROR: json for virtualizer is no array");
      return null;
    }
    for (let descriptorJSON of json) {
      const type = descriptorJSON.type;
      switch (type) {
        case 'id':
          break;
        case 'exponential':
          const center = descriptorJSON.center;
          if (center !== 'first' && center !== 'mid' && center !== 'last'
                                 && !isNaturalNumber(center)) {
            console.log(`ERROR: exponential descriptor needs to have a center field that is set to either 'first', 'mid', or 'last' or is an integer,   but it is ${center}`);
            return null;
          }
          break;
        case 'explicit':
          const remapper = descriptorJSON.remapper;
          if (!Array.isArray(remapper)) {
              console.log(`ERROR: explicit remapper descriptor needs a field 'remapper' that is an array`);
              return null;
          }
          for (let i of remapper) {
            if (!isNaturalNumber(i)) {
              console.log(`ERROR: remapper needs to contain natural numbers`);
              return null;
            }
          }
          break;
        default:
          console.log(`ERROR: descriptor needs to have a type field that
  is set to one of the values 'id', 'explicit' or 'exponential', but it is ${type}`);
          return null;
      }
    }
    return new Virtualizer(json);
  }

  toPlainJSON(schema) {
    return this._descriptorArray;
  }

  virtualize(schema) {
    this.checkAgainstSchema(schema);
    const array = this._descriptorArray.map((descriptor, order) => {
      const dimension = schema.dimensionAtOrder(order);

      const mapper = {
        'id': () => new IdentityDimensionTransformer(dimension),
        'explicit': () => explicitRemapper(dimension, descriptor.remapper),
        'exponential': () => {
            const center = indexInDimensionFromJSON(dimension, descriptor.center);
            return exponentialRemapper(dimension, center);
          }
      }[descriptor.type];
      return mapper();
    });
    return new Schema(array);
  }

  update(order, baseIndex, baseDimension) {
    const descriptor = this._descriptorArray[order];
    const currentType = descriptor.type;
    const computeNewDescriptor = {
      'id': () => { return descriptor; },
      'explicit': () => { return descriptor; },
      'exponential': () => {
          const center = indexInDimensionFromJSON(baseDimension, descriptor.center);
          if (baseIndex === center) {
            return descriptor;
          } else {
            const realIndex = jsonForDimensionFromIndex(baseDimension, baseIndex);
            return {type: 'exponential',
                    center: realIndex};
          }
        }
    }[currentType];
    const newDescriptor = computeNewDescriptor();
    const newArray = Array.from(this._descriptorArray);
    newArray[order] = newDescriptor;
    return new Virtualizer(newArray);
  }
}

