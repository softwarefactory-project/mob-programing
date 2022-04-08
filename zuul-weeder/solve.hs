{-# LANGUAGE BlockArguments #-}
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE FlexibleContexts #-}
{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE OverloadedLabels #-}
{-# LANGUAGE OverloadedStrings #-}

module Main where

import Algebra.Graph (Graph, edge, empty, overlay, vertex, vertexList)
import Algebra.Graph.ToGraph (dfs)
import Control.Lens ((%=))
import Control.Monad.State (execStateT)
import Control.Monad.State.Class (MonadState)
import Data.Foldable (traverse_)
import Data.Generics.Labels ()
import Data.Maybe (fromMaybe)
import Data.Set (Set)
import qualified Data.Set
import Data.Text (Text)
import qualified Data.Text
import Debug.Trace (trace)
import GHC.Generics (Generic)
import Witch (From, from)

data Conf
  = Pipeline {pipelineName :: PipelineName, job :: JobName}
  | Job {jobName :: JobName, parent :: (Maybe JobName), nodeset :: NodesetName}
  | Nodeset {nodesetName :: NodesetName}
  deriving (Show, Eq, Ord, Generic)

newtype PipelineName = PipelineName Text deriving (Show, Eq, Ord)

newtype JobName = JobName Text deriving (Show, Eq, Ord)

newtype NodesetName = NodesetName Text deriving (Show, Eq, Ord)

newtype ConfID = ConfID {unConf :: Text} deriving (Show, Ord, Eq)

instance From PipelineName ConfID where
  from (PipelineName n) = ConfID ("pipeline:" <> n)

instance From JobName ConfID where
  from (JobName n) = ConfID ("job:" <> n)

instance From NodesetName ConfID where
  from (NodesetName n) = ConfID ("nodeset:" <> n)

instance From Conf ConfID where
  from c = case c of
    Pipeline n _ -> from n
    Job n _ _ -> from n
    Nodeset n -> from n

readConfiguration :: Text -> Maybe Conf
readConfiguration line = do
  let (name, attrs) = Data.Text.breakOn ": " line
  kv <- readAttrs [] $ Data.Text.splitOn "=" <$> Data.Text.words attrs
  case name of
    "pipeline" -> readPipeline kv
    "job" -> readJob kv
    "nodeset" -> readNodeset kv
    _ -> Nothing
  where
    readPipeline attrs = do
      name <- lookup "name" attrs
      job <- lookup "job" attrs
      pure $ Pipeline (PipelineName name) (JobName job)

    readJob attrs = do
      name <- lookup "name" attrs
      ns <- lookup "nodeset" attrs
      pure $ Job (JobName name) (JobName <$> lookup "parent" attrs) (NodesetName ns)

    readNodeset attrs = do
      name <- lookup "name" attrs
      pure $ Nodeset (NodesetName name)

    readAttrs acc [] = Just acc
    readAttrs acc (head' : tail') = case head' of
      [k, v] -> readAttrs ((k, v) : acc) tail'
      [":"] -> readAttrs acc tail'
      _ -> Nothing

data Analysis = Analysis
  { graph :: Graph ConfID
  }
  deriving (Generic, Show)

emptyAnalysis :: Analysis
emptyAnalysis = Analysis mempty

-- | Add each configuration object to the graph
analyze :: MonadState Analysis m => Conf -> m ()
analyze object = traverse_ addEdge (mkEdges object)
  where
    addEdge (x, y) = #graph %= overlay (edge x y)
    mkEdges c = case c of
      Pipeline n job -> [(from n, from job)]
      Job job parent nodeset ->
        [(from job, from nodeset)] <> case parent of
          Just parentName -> [(from job, from parentName)]
          Nothing -> []
      _ -> []

getRoots :: [Conf] -> [ConfID]
getRoots = fmap from . filter isPipeline
  where
    isPipeline :: Conf -> Bool
    isPipeline c = case c of
      Pipeline _ _ -> True
      _ -> False

solve' :: [Conf] -> [ConfID]
solve' confs = do
  analysis <- flip execStateT emptyAnalysis do
    traverse_ analyze confs
  let roots = getRoots confs
      reachable = Data.Set.fromList $ dfs roots (graph analysis)
      allConf = Data.Set.fromList (from <$> confs)
      dead = allConf Data.Set.\\ reachable
  Data.Set.toList dead

solve :: Text -> [ConfID]
solve conf =
  solve'
    . fromMaybe (error "Invalid conf!")
    . sequence
    . map readConfiguration
    $ Data.Text.lines conf

main :: IO ()
main = print $ unConf <$> solve conf'

conf' =
  Data.Text.unlines $
    [ "job: name=job1 nodeset=ns1",
      "job: name=job2 nodeset=ns2",
      "nodeset: name=ns1",
      "nodeset: name=ns2",
      "nodeset: name=ns3",
      "pipeline: name=check job=job1"
    ]
