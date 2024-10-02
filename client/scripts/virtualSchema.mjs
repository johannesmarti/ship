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
  console.assert(0 <= center && center < baseDimension.numIndices(),
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
  constructor(descriptionArray) {
    this._descriptionArray = descriptionArray;
  }

  static fromConfiguration(configuration, length) {
    const descriptionArray = new Array(length);
    for (let order = 0; order < length; order++) {
      descriptionArray[order] = configuration[order] || {type: "id"};
    }
    return new Virtualizer(descriptionArray);
  }

  checkAgainstSchema(schema) {
    const thisLength = this._descriptionArray.length;
    console.assert(thisLength === schema.numDimensions(), 
      `schema has ${schema.numDimensions()} dimensions but virtualizer
is of length ${thisLength}`);
  }

/*
How to serialise:

[
{name: "good", type: "id"},
{name: "datatype", type: "id"},
{name: "province", type: "selection", remapper: ["Switzerland", "The
Netherlands", "Germany", "France",]},
{name: "iteration", type: "exponential", center: "iteration 12"}
]

"name" is the name of the base category
*/

  static fromJSON(schema, json) {
    const descriptionArray = new Array(schema.numDimensions());
    const orderRemapping = new Array(json.length);
    // this should give an set {0,1,2,...,schema.numDimensions() - 1}
    const leftOverOrders = new Set(Array(schema.numDimensions()).keys());
    for (let [oldOrder, jsonDescription] of json.entries()) {
      const name = jsonDescription.name;
      if (name === undefined) {
        console.log("ERROR: json description in virtualizer does not have a 'name' field.");
        return null;
      }
      const newOrder = schema.findIndex(dimension =>
                                          dimension.name() === name);
      orderRemapping[oldOrder] = newOrder;
      if (newOrder !== -1) {
        leftOverOrders.delete(newOrder);
        const dimension = schema.dimensionAtOrder(newOrder);
        const newDescription = descriptionFromJson(dimension, jsonDescription);
        if (newDescription === null) return null;
        descriptionArray[newOrder] = newDescription;
      }
      // changeDependentIndexMap
    }
    const virtualizer = new Virtualizer(descriptionArray);
    virtualizer.checkAgainstSchema(schema);
    for (const order of leftOverOrders) {
      descriptionArray[order] = {type: 'id'};
    }
    return {
      virtualizer: virtualizer,
      orderMap: o => orderRemapping[o],
      dependentIndexMap: (o,i) => orderRemapping[o],
      leftOverOrders: leftOverOrders
    };
  }

  toJSON(schema) {
    function mapper(descriptor, order) {
      const computeJSON = {
        "id": () => {
          return {
            name: schema.dimensionAtOrder(order).name();
            type: descriptor.type
          };
        },
        "exponential": () => {
          const dimension = schema.dimensionAtOrder(order);
          return {
            name: dimension.name();
            type: descriptor.type,
            center: jsonForDimensionFromIndex(dimension. descriptor.center)
          };
        }
      }
      return computeJSON[descriptor.type]
    }
    return this._descriptionArray.map(mapper);
  }

  virtualize(schema) {
    this.checkAgainstSchema(schema);
    const array = this._descriptionArray.map((descriptor, order) => {
      const dimension = schema.dimensionAtOrder(order);

      const id = () => new IdentityDimensionTransformer(dimension);
      const mapper = {
        "id": id,
        "exponential": () => {
            const center = indexInDimensionFromJSON(dimension, descriptor.center);
            return exponentialRemapper(dimension, center);
          }
      }[descriptor.type] || id;
      return mapper();
    });
    return new Schema(array);
  }

  update(order, baseIndex, baseDimension) {
    const descriptor = this._descriptionArray[order];
    const currentType = descriptor.type;
    const computeNewDescriptor = {
      "id": () => { return descriptor; },
      "exponential": () => {
          const center = indexInDimensionFromJSON(baseDimension, descriptor.center);
          if (baseIndex === center) {
            return descriptor;
          } else {
            const realIndex = jsonForDimensionFromIndex(baseDimension, baseIndex);
            return {type: "exponential",
                    center: realIndex};
          }
        }
    }[currentType];
    const newDescriptor = computeNewDescriptor();
    const newArray = Array.from(this._descriptionArray);
    newArray[order] = newDescriptor;
    return new Virtualizer(newArray);
  }
}

