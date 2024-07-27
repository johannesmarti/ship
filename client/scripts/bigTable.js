console.log("bigTable starts loading");

function createCategory(spec) {
  const name = spec.name;
  const nameList = spec.indices;
  console.assert(nameList.length >= 1,
    f"Need at least one index in category {name}");

  function isIndex(number) {
    return 0 <= number && number < nameList.length;
  }

  return {
    name: function() { return name; },

    nameOfIndex: function(index) {
      console.assert(isIndex(index), `{index} is not an index in category`);
      return nameList[index];
    },

    indexOfName: function(name) {
      return nameList.indexOf(name);
    },

    indices: function*() {
      for (let index = 0; index < nameList.length; index++) {
        yield index;
      }
    },

    numIndices: function() {
      return nameList.length;
    }
  };
}

function createSchema(spec) {
  const numCategories = spec.length;
  const categories = spec.map(createCategory);

  function isOrder(number) {
    return 0 <= number && number < numCategories;
  }

  return {
    orders: function*() {
      for (let order = 0; order < numCategories; order++) {
        yield order;
      }
    },
    numCategories: function() { return numCategories; },
    categoryOfOrder: function(order) {
      console.assert(isOrder(order), `{order} is not an order in schema`);
      return categories[order];
    },
    orderOfCategoryName: function(categoryName) {
      return categories.findIndex((c) => c.name() = categoryName);
    }
  };
}

function lookup(address) {
  console.log(address);
  const sum = address.reduce((accum, value) => accum + value, 0);
  console.log(sum);
  return sum;
}

//function createBigTable(schema, lookup) {

function h(tagName, ...args) {
  const el = document.createElement(tagName);
  el.append(...args);
  return el;
}

console.log("bigTable loaded");

