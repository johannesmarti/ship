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

class FixedValueDimensionTransformer {
  constructor(baseDimension, fixedIndex) {
    this._baseDimension = baseDimension;
    this._fixedIndex = fixedIndex;
  }

  nameOfFixedIndex() {
    return this._baseDimension.nameOfIndex(this._fixedIndex);
  }

  numIndices() {
    return 1;
  }

  isIndex(number) {
    return 0 <= number && number < this.numIndices();
  }

  name() {
    return this._baseDimension.name() + `[${this.nameOfFixedIndex()}]`;
  }

  nameOfIndex(index) {
    console.assert(index === 0,
      `${index} is not a index in the fixed dimension ${this.name()} because it is not equal to 0`);
    return this.nameOfFixedIndex(); 
  }

  transform(index) {
    return this._fixedIndex;
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

class TransformedDataView {
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

export class Virtualizer {
  constructor(configuration) {
    this._configuration = configuration;
  }

  configuration() {
    return this._configuration;
  }

  virtualize(schema) {
    const array = schema._dimensions.map((_, o) => {
      const dimension = schema.dimensionAtOrder(o);
      const descriptor = this._configuration[o] || {"type": "id"};

      const id = () => new IdentityDimensionTransformer(dimension);
      const onFixed = () => {
            const fixedValue = indexInDimensionFromJSON(dimension, descriptor["value"]);
            return new FixedValueDimensionTransformer(dimension, fixedValue);
      };
      const mapper = {
        "id": id,
        "fixed": onFixed,
        "fixed_id": onFixed,
        "fixed_exponential": onFixed,
        "exponential": () => {
            const center = indexInDimensionFromJSON(dimension, descriptor["center"]);
            return exponentialRemapper(dimension, center);
          }
      }[descriptor["type"]] || id;
      return mapper();
    });
    return new Schema(array);
  }

  update(order, baseIndex, baseDimension) {
    const configuration = this.configuration();
    const description = configuration[order] || {"type": "id"};
    const currentType = description["type"] || "id";
    const computeNewDescription = {
      "id": () => { return {"type": "fixed_id", "value": baseIndex}; },
      "fixed": () => { return {"type": "id"}; },
      "fixed_id": () => { return {"type": "id"}; },
      "fixed_exponential": () => {
          return {"type": "exponential",
                  "center": description["value"]};
        },
      "exponential": () => {
          const center = indexInDimensionFromJSON(baseDimension,
            description["center"]);
          if (baseIndex === center) {
            return {"type": "fixed_exponential",
                    "value": description["center"]};
          } else {
            return {"type": "exponential",
                    // TODO: Here we could make an effort to
                    // reconstruct the JSON descriptors "first",
                    // "mid" and "last".
                    "center": baseIndex};
          }
        }
    }[currentType];
    const newDescription = computeNewDescription()
    const newConfiguration = { ...configuration, [order]: newDescription};
    const newVirtualizer = new Virtualizer(newConfiguration);
    return newVirtualizer;
  }
}

