{-# LANGUAGE LambdaCase #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QualifiedDo #-}
{-# LANGUAGE RecordWildCards #-}

module Main where

import Control.Monad (void)
import Control.Monad.State
import Data.Function ((&))
import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map
import Data.Text (Text, pack)
import Lens.Micro ((^?!))
import Lens.Micro.Aeson (key, _String)
import qualified System.Posix.Signals as Signals
import System.Environment (getEnv)

import Slacker
import qualified Slacker as S

main :: IO ()
main = do
    (apiToken, appToken) <- (,) <$> getEnv "SLACK_BOT_TOKEN" <*> getEnv "SLACK_APP_TOKEN"

    let cfg =
            defaultSlackConfig
                & setApiToken (pack apiToken)
                & setAppToken (pack appToken)
                & setGracefulShutdownHandler handleShutdown
                & setOnException handleThreadExceptionSensibly
                & setLogLevel (Just LevelDebug)
    void $ runStateT (runSocketMode cfg handler) (ThreadsCounter mempty)

handleShutdown :: IO () -> IO ()
handleShutdown shutdown = do
    void $ Signals.installHandler Signals.sigTERM (Signals.CatchOnce shutdown) Nothing
    void $ Signals.installHandler Signals.sigINT (Signals.CatchOnce shutdown) Nothing

newtype ThreadsCounter = ThreadsCounter (Map Text Int)

handler :: SlackConfig -> SocketModeEvent -> StateT ThreadsCounter IO ()
handler cfg = \case
    Event AppMention{..} ->
        postMessage cfg . toThread channel ts . blocks_ $ S.do
            section_ $ S.do
                "A button!"
                button_ "Blue pill" "blue-action"
            section_ $ S.do
                button_ "Red pill" "red-action"
    BlockAction "blue-action" val -> do
        let url = val ^?! key "response_url" . _String
        respondMessage url "You took the blue button!"
    BlockAction "red-action" val -> do
        let url = val ^?! key "response_url" . _String
        respondMessage url "You clicked the red button!"
    evt -> liftIO (print evt)
