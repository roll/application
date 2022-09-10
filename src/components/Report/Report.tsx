import React, { useState } from 'react'
import { IReport } from '../../interfaces'
import { ThemeProvider } from '@mui/material/styles'
import * as themes from '../../themes'
import Task from './Task'

export interface ReportProps {
  /**
   * Report object i.e. generated by `frictionless.validate`
   */
  report: IReport
  /**
   * Whether to show the debug form
   */
  debug?: boolean
}

/**
 * Visual component for Frictionless Report rendering
 */
export default function Report(props: ReportProps) {
  const { debug } = props
  const [report, setReport] = useState(props.report)
  const tasks = getSortedTasks(report)
  return (
    <ThemeProvider theme={themes.DEFAULT}>
      <div className="frictionless-components-report">
        {/* Form */}
        {!!debug && (
          <textarea
            className="form-control debug"
            value={JSON.stringify(report, null, 2)}
            onChange={(ev) => setReport(JSON.parse(ev.target.value))}
          ></textarea>
        )}

        {/* Errors */}
        {!!report.errors.length && (
          <div className="file error">
            <h4 className="file-heading">
              <div className="inner">
                <a className="file-name">
                  <strong>Errors</strong>
                </a>
              </div>
            </h4>
            <ul className="passed-tests result">
              {report.errors.map((error, index) => (
                <li key={index}>
                  <span className="badge badge-error">{error.message}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Tasks */}
        {tasks.map((task, index) => (
          <Task
            key={index}
            task={task}
            taskNumber={index + 1}
            tasksCount={tasks.length}
          />
        ))}
      </div>
    </ThemeProvider>
  )
}

// Helpers

function getSortedTasks(report: IReport) {
  return [
    ...report.tasks.filter((task) => !task.valid),
    ...report.tasks.filter((task) => task.valid),
  ]
}
