import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import PromptAnalysis from "./pages/PromptAnalysis";
import ModulePage from "./pages/ModulePage";

import "./App.css";

function App() {
    return (
        <BrowserRouter>
            <Routes>

                <Route element={<Layout />}>

                    <Route
                        path="/"
                        element={<Dashboard />}
                    />

                    <Route
                        path="/prompt-analysis"
                        element={<PromptAnalysis />}
                    />

                    <Route
                        path="/runtime-monitoring"
                        element={
                            <ModulePage
                                title="Runtime Monitoring"
                                description="Monitor AI agent runtime activity, tool calls, API requests and security events."
                                icon="◉"
                            />
                        }
                    />

                    <Route
                        path="/alerts"
                        element={
                            <ModulePage
                                title="Security Alerts"
                                description="View and manage detected security threats and security alerts."
                                icon="⚠"
                            />
                        }
                    />

                    <Route
                        path="/reports"
                        element={
                            <ModulePage
                                title="Security Reports"
                                description="Generate and review security analysis reports."
                                icon="▤"
                            />
                        }
                    />

                    <Route
                        path="/settings"
                        element={
                            <ModulePage
                                title="Settings"
                                description="Configure AI Agent Security Platform settings."
                                icon="⚙"
                            />
                        }
                    />

                </Route>

            </Routes>
        </BrowserRouter>
    );
}

export default App;