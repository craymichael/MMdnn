# ----------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License.txt in the project root for license information.
# ----------------------------------------------------------------------------------------------
import os
import tensorflow.keras as _keras
from tensorflow import nest
from mmdnn.conversion.common.DataStructure.graph import GraphNode, Graph


class TFKeras2GraphNode(GraphNode):

    def __init__(self, layer):
        super(TFKeras2GraphNode, self).__init__(layer)

    @property
    def name(self):
        return self.layer.name

    @property
    def type(self):
        return self.layer.__class__.__name__

    @property
    def keras_layer(self):
        return self.layer


class TFKeras2Graph(Graph):

    def __init__(self, model):
        # sanity check.
        # if not (type(model) == _keras.models.Sequential or type(model) == _keras.models.Model):
        if not isinstance(model,
                          (_keras.models.Sequential, _keras.models.Model)):
            raise TypeError(
                "Keras layer of type %s is not supported." % type(model))
        super(TFKeras2Graph, self).__init__(model)
        self.model = model

    def build(self):
        self.input_layers = list()
        for i, layer in enumerate(self.model.layers):
            self.layer_map[layer.name] = TFKeras2GraphNode(layer)
            self.layer_name_map[layer.name] = layer.name
            for node in layer._inbound_nodes:
                for pred in nest.flatten(node.inbound_layers):
                    if pred.name not in self.layer_map:
                        self.layer_map[pred.name] = TFKeras2GraphNode(pred)
                        self.layer_name_map[pred.name] = pred.name
                    self._make_connection(pred.name, layer.name)

        # Kit: TODO
        # Duplicate models for weight sharing
        # Expand the sub-models
        super(TFKeras2Graph, self).build()
